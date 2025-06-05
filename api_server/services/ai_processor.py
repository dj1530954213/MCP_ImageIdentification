"""
MCP图像识别系统 - AI处理服务模块

这个模块负责协调整个AI处理流程，包括：
1. 通过MCP获取简道云数据
2. 调用图像识别服务
3. 使用AI模型处理识别结果
4. 通过MCP保存处理结果

重要原则：
- 所有简道云数据操作都通过MCP服务器进行
- 绝对不允许直接调用简道云API
- 详细记录每个处理步骤
- 提供完整的错误处理

处理流程：
数据获取(MCP) -> 图像识别(Mock/Real) -> AI处理(Qwen3) -> 数据保存(MCP)

作者：MCP图像识别系统
版本：1.0.0
"""

import asyncio
import time
from typing import Dict, Any, List

from api_server.config.settings import settings
from api_server.models.models import (
    ProcessResult, ProcessStatus, VisionResult, AIProcessResult, VisionResultType
)
from api_server.services.mcp_client import mcp_client_service
from api_server.providers.vision_provider import mock_vision_provider
from api_server.providers.local_ai_provider import local_ai_provider

class AIProcessorService:
    """
    AI处理服务类
    
    这个类协调整个AI处理流程，确保所有操作都按照正确的顺序执行。
    它严格遵循MCP架构，所有简道云操作都通过MCP服务器进行。
    
    主要职责：
    1. 流程协调：管理整个处理流程的执行顺序
    2. 数据获取：通过MCP从简道云获取数据
    3. 图像识别：调用图像识别服务处理图像
    4. AI处理：使用本地AI模型处理识别结果
    5. 数据保存：通过MCP将结果保存到简道云
    6. 错误处理：处理各个环节可能出现的错误
    """
    
    def __init__(self):
        """
        初始化AI处理服务
        
        注入所需的依赖服务：
        - MCP客户端：用于简道云数据操作
        - 图像识别提供者：当前使用Mock实现
        - AI提供者：使用本地Qwen3模型
        """
        self.mcp_client = mcp_client_service
        self.vision_provider = mock_vision_provider  # 当前使用Mock实现
        self.ai_provider = local_ai_provider
    
    async def process_record(self, record_id: str, force_reprocess: bool = False) -> ProcessResult:
        """
        处理指定记录的完整流程
        
        这是系统的核心方法，执行完整的AI处理流程。
        严格按照MCP架构，所有简道云操作都通过MCP服务器进行。
        
        Args:
            record_id: 记录ID，用于标识要处理的记录
            force_reprocess: 是否强制重新处理
            
        Returns:
            ProcessResult: 完整的处理结果
        """
        start_time = time.time()
        
        try:
            print(f"\n🎯 ===== 开始完整AI处理流程 =====")
            print(f"📋 处理记录ID: {record_id}")
            print(f"🔄 强制重新处理: {force_reprocess}")
            print(f"⚠️ 重要声明：本流程严格通过MCP服务器，绝不直接调用简道云API")
            print(f"⚠️ 所有数据读写操作都通过MCP工具：query_data 和 process_and_save")
            
            # 步骤1：通过MCP获取记录数据
            print(f"\n📥 步骤1：通过MCP获取记录数据")
            record_data = await self._get_record_data(record_id)
            
            if not record_data.get("success"):
                print(f"❌ 步骤1失败：MCP数据获取失败")
                return ProcessResult(
                    success=False,
                    record_id=record_id,
                    status=ProcessStatus.FAILED,
                    error_message=record_data.get("error", "获取记录失败"),
                    processing_time=time.time() - start_time
                )
            
            data = record_data["data"]
            print(f"✅ 记录数据获取成功: {data.get('source_text', '')[:50]}...")
            
            # 步骤2：图像识别处理
            print(f"\n👁️ 步骤2：图像识别处理")
            vision_result = await self._process_vision(data)
            print(f"✅ 图像识别完成: {vision_result.type} - {vision_result.confidence:.2f}")
            
            # 步骤3：AI处理
            print(f"\n🤖 步骤3：AI处理")
            ai_result = await self._process_ai(vision_result, data.get("source_text", ""))
            print(f"✅ AI处理完成: {ai_result.processed_text[:50]}...")
            
            # 步骤4：通过MCP保存数据
            print(f"\n💾 步骤4：通过MCP保存数据")
            update_result = await self._update_record(record_id, ai_result, vision_result)
            
            if not update_result.get("success"):
                print(f"❌ 步骤4失败：MCP数据保存失败")
                return ProcessResult(
                    success=False,
                    record_id=record_id,
                    status=ProcessStatus.FAILED,
                    vision_result=vision_result,
                    ai_result=ai_result,
                    error_message=update_result.get("error", "数据回写失败"),
                    processing_time=time.time() - start_time
                )
            
            print("✅ 数据回写成功")
            
            # 步骤5：返回成功结果
            total_time = time.time() - start_time
            print(f"🎉 处理完成，总耗时: {total_time:.2f}秒")
            print(f"🔚 ===== AI处理流程完成 =====\n")
            
            return ProcessResult(
                success=True,
                record_id=record_id,
                status=ProcessStatus.SUCCESS,
                vision_result=vision_result,
                ai_result=ai_result,
                processing_time=total_time
            )
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            return ProcessResult(
                success=False,
                record_id=record_id,
                status=ProcessStatus.FAILED,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
    
    async def _get_record_data(self, record_id: str) -> Dict[str, Any]:
        """
        通过MCP获取记录数据
        
        这个方法调用MCP客户端来获取简道云数据。
        绝对不会直接调用简道云API。
        
        Args:
            record_id: 记录ID
            
        Returns:
            Dict[str, Any]: 包含获取结果的字典
        """
        try:
            print(f"\n🔍 ===== AI处理器：开始获取数据 =====")
            print(f"📋 请求记录ID: {record_id}")
            print(f"📡 调用MCP客户端获取数据...")
            print(f"⚠️ 注意：此处绝对不会直接调用简道云API，只通过MCP服务器")
            
            result = await self.mcp_client.get_record(record_id)
            
            if result.get("success"):
                data = result.get("data", {})
                print(f"✅ MCP数据获取成功")
                if isinstance(data, dict):
                    print(f"📄 源文本预览: {str(data.get('source_text', ''))[:100]}...")
                elif isinstance(data, list):
                    print(f"📊 数据条数: {len(data)}")
            else:
                print(f"❌ MCP数据获取失败: {result.get('error', '未知错误')}")
            
            print(f"🔚 ===== AI处理器：数据获取完成 =====\n")
            return result
        except Exception as e:
            error_msg = f"MCP获取数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _process_vision(self, record_data: Dict[str, Any]) -> VisionResult:
        """
        处理图像识别
        
        调用图像识别服务处理图像数据。
        当前使用Mock实现，未来可以替换为真实的图像识别服务。
        
        Args:
            record_data: 记录数据
            
        Returns:
            VisionResult: 图像识别结果
        """
        try:
            print(f"👁️ 开始图像识别处理...")
            if settings.USE_MOCK_VISION:
                print(f"📝 使用Mock图像识别服务")
                result = await self.vision_provider.recognize(record_data)
                print(f"✅ Mock图像识别完成")
                return result
            else:
                # 这里后续集成真实的图像识别服务
                print(f"🚧 真实图像识别服务尚未实现")
                raise NotImplementedError("真实图像识别服务尚未实现")
                
        except Exception as e:
            print(f"❌ 图像识别失败: {e}")
            # 如果图像识别失败，返回一个默认结果
            return VisionResult(
                type=VisionResultType.DOCUMENT_ANALYSIS,
                content=f"图像识别失败: {str(e)}",
                confidence=0.1,
                details={"error": str(e)},
                processing_time=0.1
            )

    async def _process_ai(self, vision_result: VisionResult, original_text: str) -> AIProcessResult:
        """
        处理AI分析

        使用本地AI模型（Qwen3:1.7b）处理图像识别结果。

        Args:
            vision_result: 图像识别结果
            original_text: 原始文本

        Returns:
            AIProcessResult: AI处理结果
        """
        try:
            print(f"🤖 开始AI处理...")
            if settings.USE_LOCAL_AI:
                print(f"🧠 使用本地AI模型: {settings.LOCAL_AI_MODEL}")
                result = await self.ai_provider.process_vision_result(
                    vision_result.model_dump(),  # 使用model_dump替代dict()
                    original_text
                )
                print(f"✅ 本地AI处理完成")
                return result
            else:
                print(f"📝 使用简单文本处理方案")
                # 如果不使用本地AI，使用简单的文本处理
                return self._simple_text_processing(vision_result, original_text)

        except Exception as e:
            print(f"❌ AI处理失败: {e}")
            # 如果AI处理失败，使用备用方案
            return AIProcessResult(
                original_text=original_text,
                processed_text=f"[处理失败] {vision_result.content[:100]}...",
                ai_analysis=f"AI处理失败: {str(e)}",
                confidence=0.1,
                processing_time=0.1
            )

    def _simple_text_processing(self, vision_result: VisionResult, original_text: str) -> AIProcessResult:
        """
        简单的文本处理（备用方案）

        当AI模型不可用时使用的简单文本处理逻辑。

        Args:
            vision_result: 图像识别结果
            original_text: 原始文本

        Returns:
            AIProcessResult: 简单处理的结果
        """
        print(f"📝 执行简单文本处理...")

        processed_text = f"[简单处理] {vision_result.content}"

        return AIProcessResult(
            original_text=original_text,
            processed_text=processed_text,
            ai_analysis="使用简单文本处理方案",
            confidence=0.7,
            processing_time=0.1
        )

    async def _update_record(self, record_id: str, ai_result: AIProcessResult, vision_result: VisionResult) -> Dict[str, Any]:
        """
        通过MCP更新记录数据

        这个方法调用MCP客户端来保存处理结果到简道云。
        绝对不会直接调用简道云API。

        Args:
            record_id: 记录ID
            ai_result: AI处理结果
            vision_result: 图像识别结果

        Returns:
            Dict[str, Any]: 包含更新结果的字典
        """
        try:
            print(f"\n💾 ===== AI处理器：开始保存数据 =====")
            print(f"📋 目标记录ID: {record_id}")

            # 构造更新数据
            updates = {
                "original_text": ai_result.original_text,
                "processed_text": ai_result.processed_text,
                "vision_type": vision_result.type,
                "vision_confidence": vision_result.confidence,
                "ai_confidence": ai_result.confidence,
                "processing_status": "completed"
            }

            print(f"📄 构造的更新数据:")
            print(f"   - 原始文本长度: {len(updates['original_text'])} 字符")
            print(f"   - 处理文本长度: {len(updates['processed_text'])} 字符")
            print(f"   - 原始文本预览: {updates['original_text'][:50]}...")
            print(f"   - 处理文本预览: {updates['processed_text'][:50]}...")
            print(f"   - 视觉类型: {updates['vision_type']}")
            print(f"   - 视觉置信度: {updates['vision_confidence']:.3f}")
            print(f"   - AI置信度: {updates['ai_confidence']:.3f}")
            print(f"   - 处理状态: {updates['processing_status']}")

            print(f"📡 调用MCP客户端保存数据...")
            print(f"⚠️ 注意：此处绝对不会直接调用简道云API，只通过MCP服务器")

            result = await self.mcp_client.update_record(record_id, updates)

            print(f"📨 MCP客户端保存返回结果:")
            print(f"   - 成功状态: {result.get('success')}")
            print(f"   - 结果类型: {type(result)}")
            print(f"   - 结果字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")

            if result.get("success"):
                print("✅ MCP数据保存成功")
                api_response = result.get("api_response")
                if api_response:
                    print(f"📋 MCP服务器返回的简道云API响应:")
                    print(f"   - 响应类型: {type(api_response)}")
                    print(f"   - 响应内容: {str(api_response)[:200]}...")
            else:
                print(f"❌ MCP数据保存失败: {result.get('error', '未知错误')}")

            print(f"🔚 ===== AI处理器：数据保存完成 =====\n")
            return result

        except Exception as e:
            error_msg = f"MCP更新数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg
            }

    async def batch_process(self, record_ids: List[str]) -> Dict[str, Any]:
        """
        批量处理记录

        并发处理多个记录，控制并发数量以避免系统过载。

        Args:
            record_ids: 要处理的记录ID列表

        Returns:
            Dict[str, Any]: 批量处理结果
        """
        start_time = time.time()
        success_count = 0
        failed_count = 0

        print(f"🔄 开始批量处理 {len(record_ids)} 条记录...")

        # 控制并发数量
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

        async def process_single(record_id: str):
            """处理单个记录的包装函数"""
            async with semaphore:
                return await self.process_record(record_id)

        # 并发处理
        tasks = [process_single(record_id) for record_id in record_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
            elif result.success:
                success_count += 1
            else:
                failed_count += 1

        total_time = time.time() - start_time

        print(f"🎉 批量处理完成: 成功 {success_count}, 失败 {failed_count}, 耗时 {total_time:.2f}秒")

        return {
            "success": True,
            "total_count": len(record_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": [r for r in results if not isinstance(r, Exception)],
            "processing_time": total_time
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        检查所有依赖服务的健康状态。

        Returns:
            Dict[str, Any]: 健康检查结果
        """
        health_results = {}
        overall_healthy = True

        # 检查MCP连接
        try:
            mcp_health = await self.mcp_client.health_check()
            health_results["mcp"] = mcp_health
            if mcp_health.get("status") != "healthy":
                overall_healthy = False
        except Exception as e:
            health_results["mcp"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # 检查图片识别服务
        try:
            vision_health = await self.vision_provider.health_check()
            health_results["vision"] = vision_health
            if vision_health.get("status") != "healthy":
                overall_healthy = False
        except Exception as e:
            health_results["vision"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # 检查AI服务
        try:
            ai_health = await self.ai_provider.health_check()
            health_results["ai"] = ai_health
            if ai_health.get("status") != "healthy":
                overall_healthy = False
        except Exception as e:
            health_results["ai"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "services": health_results,
            "model_info": {
                "ai_model": settings.LOCAL_AI_MODEL,
                "vision_provider": "mock" if settings.USE_MOCK_VISION else "real",
                "use_local_ai": settings.USE_LOCAL_AI
            }
        }

# ==================== 全局AI处理服务实例 ====================
# 创建全局AI处理服务实例，整个应用程序共享使用
ai_processor_service = AIProcessorService()
