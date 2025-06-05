"""
本地AI模型提供者
支持通过Ollama调用本地部署的AI模型
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional
from api_server.config.settings import settings
from api_server.models.models import AIProcessResult

class LocalAIProvider:
    """本地AI模型提供者"""
    
    def __init__(self):
        self.base_url = settings.LOCAL_AI_BASE_URL
        self.model = settings.LOCAL_AI_MODEL
        self.timeout = 60  # 60秒超时
        
    async def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用Ollama API
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Returns:
            str: AI响应
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
                
            except httpx.TimeoutException:
                raise Exception(f"AI模型调用超时 (>{self.timeout}秒)")
            except httpx.HTTPStatusError as e:
                raise Exception(f"AI模型调用失败: HTTP {e.response.status_code}")
            except Exception as e:
                raise Exception(f"AI模型调用错误: {str(e)}")
    
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
