"""
MCP图像识别系统 - 本地AI模型提供者模块

这个模块提供本地AI模型的调用接口，主要通过Ollama框架调用本地部署的AI模型。
支持多种AI模型，当前主要使用Qwen3:1.7b模型进行文本处理和分析。

主要功能：
1. 调用本地AI模型进行文本处理
2. 处理图像识别结果并生成智能分析
3. 提供健康检查和模型测试功能
4. 支持备用处理方案

技术特点：
- 基于Ollama API进行模型调用
- 异步处理提高性能
- 完整的错误处理和超时控制
- 支持自定义提示词和参数
- 提供详细的处理分析

支持的模型：
- Qwen3:1.7b（默认）
- 其他Ollama支持的模型

作者：MCP图像识别系统
版本：1.0.0
"""

import asyncio                                    # 异步编程支持
import json                                       # JSON数据处理
import httpx                                      # 异步HTTP客户端
from typing import Dict, Any, Optional           # 类型注解
from api_server.config.settings import settings  # 配置设置
from api_server.models.models import AIProcessResult  # 数据模型

class LocalAIProvider:
    """
    本地AI模型提供者

    这个类封装了与本地AI模型的交互逻辑，通过Ollama API调用本地部署的AI模型。
    主要用于处理图像识别结果，生成智能化的文本分析和格式化输出。

    核心功能：
    - AI模型调用：通过HTTP API调用本地AI模型
    - 结果处理：智能处理图像识别结果
    - 文本生成：生成格式化的处理结果
    - 健康监控：提供模型健康检查功能
    """

    def __init__(self):
        """
        初始化本地AI提供者

        从配置中读取AI模型相关设置，包括API地址、模型名称和超时时间。
        """
        # ==================== 基础配置 ====================
        self.base_url = settings.LOCAL_AI_BASE_URL    # Ollama API基础URL
        self.model = settings.LOCAL_AI_MODEL          # 使用的AI模型名称
        self.timeout = 60                             # HTTP请求超时时间（秒）

        print(f"🤖 本地AI提供者初始化完成")
        print(f"📡 API地址: {self.base_url}")
        print(f"🧠 模型名称: {self.model}")
        print(f"⏰ 超时设置: {self.timeout}秒")
        
    async def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用Ollama API进行AI模型推理

        这是与本地AI模型交互的核心方法，通过HTTP API调用Ollama服务。
        支持自定义系统提示词和用户提示词，可以控制模型的行为和输出格式。

        Args:
            prompt: 用户提示词，描述具体的任务和要求
            system_prompt: 系统提示词，定义AI的角色和行为规范

        Returns:
            str: AI模型生成的响应文本

        Raises:
            Exception: 当API调用失败、超时或网络错误时抛出异常
        """
        # ==================== 构造API请求 ====================
        url = f"{self.base_url}/api/generate"

        # 构造请求负载，包含模型参数和生成选项
        payload = {
            "model": self.model,                          # 指定使用的AI模型
            "prompt": prompt,                             # 用户提示词
            "stream": False,                              # 不使用流式输出
            "options": {                                  # 生成参数
                "temperature": 0.7,                       # 控制输出的随机性（0-1）
                "top_p": 0.9,                            # 核采样参数
                "max_tokens": 1000                        # 最大生成token数
            }
        }

        # 如果提供了系统提示词，添加到请求中
        if system_prompt:
            payload["system"] = system_prompt

        # ==================== 执行HTTP请求 ====================
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # 发送POST请求到Ollama API
                response = await client.post(url, json=payload)
                response.raise_for_status()  # 检查HTTP状态码

                # 解析JSON响应并提取生成的文本
                result = response.json()
                ai_response = result.get("response", "")

                print(f"✅ AI模型调用成功，响应长度: {len(ai_response)} 字符")
                return ai_response

            except httpx.TimeoutException:
                # 请求超时异常
                error_msg = f"AI模型调用超时 (>{self.timeout}秒)"
                print(f"⏰ {error_msg}")
                raise Exception(error_msg)
            except httpx.HTTPStatusError as e:
                # HTTP状态码错误
                error_msg = f"AI模型调用失败: HTTP {e.response.status_code}"
                print(f"🌐 {error_msg}")
                raise Exception(error_msg)
            except Exception as e:
                # 其他异常
                error_msg = f"AI模型调用错误: {str(e)}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
    
    async def process_vision_result(self, vision_result: Dict[str, Any], original_text: str = "") -> AIProcessResult:
        """
        处理图片识别结果
        
        Args:
            vision_result: 图片识别结果
            original_text: 原始文本
            
        Returns:
            AIProcessResult: AI处理结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 构造系统提示
            system_prompt = """你是一个专业的数据处理助手。你的任务是：
1. 分析图片识别的结果
2. 提取关键信息
3. 格式化输出，添加适当的标识
4. 确保输出简洁明了

请用中文回复，保持专业和准确。"""
            
            # 构造用户提示
            user_prompt = f"""
请分析以下图片识别结果，并进行处理：

原始文本: {original_text}

图片识别结果:
- 识别类型: {vision_result.get('type', '未知')}
- 识别内容: {vision_result.get('content', '无内容')}
- 置信度: {vision_result.get('confidence', 0)}

请根据识别结果生成一个处理后的文本，格式为: [AI识别] + 关键信息摘要

要求:
1. 提取最重要的信息
2. 保持简洁明了
3. 添加[AI识别]标识
4. 如果是身份证等敏感信息，请适当脱敏
"""
            
            # 调用AI模型
            ai_response = await self._call_ollama(user_prompt, system_prompt)
            
            # 处理AI响应
            processed_text = self._format_ai_response(ai_response, vision_result)
            
            # 计算处理时间
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # 生成AI分析
            ai_analysis = self._generate_analysis(vision_result, ai_response)
            
            return AIProcessResult(
                original_text=original_text,
                processed_text=processed_text,
                ai_analysis=ai_analysis,
                confidence=min(0.95, vision_result.get('confidence', 0.8) * 0.9),  # 稍微降低置信度
                processing_time=processing_time
            )
            
        except Exception as e:
            # 如果AI处理失败，使用备用方案
            return self._fallback_processing(vision_result, original_text, str(e))
    
    def _format_ai_response(self, ai_response: str, vision_result: Dict[str, Any]) -> str:
        """格式化AI响应"""
        
        # 清理AI响应
        cleaned_response = ai_response.strip()
        
        # 如果AI响应已经包含[AI识别]标识，直接返回
        if "[AI识别]" in cleaned_response:
            return cleaned_response
        
        # 否则添加标识
        if cleaned_response:
            return f"[AI识别] {cleaned_response}"
        else:
            # 如果AI响应为空，使用备用格式
            content = vision_result.get('content', '无法识别内容')
            return f"[AI识别] {content[:100]}..."  # 截取前100字符
    
    def _generate_analysis(self, vision_result: Dict[str, Any], ai_response: str) -> str:
        """生成AI分析结果"""
        
        vision_type = vision_result.get('type', '未知')
        confidence = vision_result.get('confidence', 0)
        
        analysis_parts = []
        
        # 识别类型分析
        type_analysis = {
            'text_recognition': '文字识别',
            'object_detection': '物体检测', 
            'document_analysis': '文档分析',
            'face_recognition': '人脸识别',
            'mock': 'Mock测试'
        }
        
        analysis_parts.append(f"识别类型: {type_analysis.get(vision_type, vision_type)}")
        
        # 置信度分析
        if confidence >= 0.9:
            confidence_desc = "高置信度"
        elif confidence >= 0.7:
            confidence_desc = "中等置信度"
        else:
            confidence_desc = "低置信度"
        
        analysis_parts.append(f"识别质量: {confidence_desc} ({confidence:.2f})")
        
        # AI处理状态
        if ai_response and len(ai_response.strip()) > 10:
            analysis_parts.append("AI处理: 成功完成智能分析和格式化")
        else:
            analysis_parts.append("AI处理: 使用备用处理方案")
        
        return " | ".join(analysis_parts)
    
    def _fallback_processing(self, vision_result: Dict[str, Any], original_text: str, error: str) -> AIProcessResult:
        """备用处理方案"""
        
        # 简单的文本处理
        content = vision_result.get('content', original_text)
        processed_text = f"[AI识别] {content[:200]}..."  # 截取前200字符
        
        return AIProcessResult(
            original_text=original_text,
            processed_text=processed_text,
            ai_analysis=f"AI处理失败，使用备用方案: {error}",
            confidence=0.5,  # 降低置信度
            processing_time=0.1
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试简单的AI调用
            test_prompt = "请回复'健康检查通过'"
            response = await self._call_ollama(test_prompt)
            
            return {
                "status": "healthy",
                "model": self.model,
                "base_url": self.base_url,
                "response_preview": response[:50] + "..." if len(response) > 50 else response,
                "version": "1.0.0"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model,
                "base_url": self.base_url,
                "error": str(e),
                "version": "1.0.0"
            }
    
    async def test_model(self) -> Dict[str, Any]:
        """测试模型功能"""
        try:
            test_cases = [
                {
                    "name": "基础对话测试",
                    "prompt": "你好，请简单介绍一下你自己。",
                    "expected_keywords": ["助手", "帮助", "AI"]
                },
                {
                    "name": "数据处理测试", 
                    "prompt": "请为以下文本添加[AI识别]标识：身份证号码123456789",
                    "expected_keywords": ["AI识别", "身份证"]
                }
            ]
            
            results = []
            
            for test_case in test_cases:
                try:
                    response = await self._call_ollama(test_case["prompt"])
                    
                    # 检查关键词
                    keywords_found = [kw for kw in test_case["expected_keywords"] if kw in response]
                    
                    results.append({
                        "name": test_case["name"],
                        "success": len(keywords_found) > 0,
                        "response_length": len(response),
                        "keywords_found": keywords_found,
                        "response_preview": response[:100] + "..." if len(response) > 100 else response
                    })
                    
                except Exception as e:
                    results.append({
                        "name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
            
            success_count = sum(1 for r in results if r.get("success", False))
            
            return {
                "overall_success": success_count == len(test_cases),
                "success_rate": f"{success_count}/{len(test_cases)}",
                "model": self.model,
                "test_results": results
            }
            
        except Exception as e:
            return {
                "overall_success": False,
                "error": str(e),
                "model": self.model
            }

# 创建全局实例
local_ai_provider = LocalAIProvider()
