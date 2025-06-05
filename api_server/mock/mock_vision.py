"""
Mock图片识别服务
用于开发和测试阶段，模拟真实的图片识别功能
"""

import random
import asyncio
from datetime import datetime
from typing import Dict, Any
from api_server.models.response_models import VisionResult, VisionResultType

class MockVisionProvider:
    """Mock图片识别提供者"""
    
    def __init__(self):
        self.mock_results = self._init_mock_results()
    
    def _init_mock_results(self) -> list:
        """初始化Mock结果数据"""
        return [
            {
                "type": VisionResultType.TEXT_RECOGNITION,
                "content": "身份证号码: 123456789012345678\n姓名: 张三\n性别: 男",
                "confidence": 0.95,
                "details": {
                    "detected_text_count": 3,
                    "language": "zh",
                    "document_type": "id_card"
                }
            },
            {
                "type": VisionResultType.TEXT_RECOGNITION,
                "content": "合同编号: HT2025001\n甲方: ABC公司\n乙方: XYZ公司\n签署日期: 2025-06-05",
                "confidence": 0.88,
                "details": {
                    "detected_text_count": 4,
                    "language": "zh",
                    "document_type": "contract"
                }
            },
            {
                "type": VisionResultType.OBJECT_DETECTION,
                "content": "检测到物体: 汽车(2辆), 人员(3人), 建筑物(1栋), 交通标志(2个)",
                "confidence": 0.92,
                "details": {
                    "objects": [
                        {"name": "汽车", "count": 2, "confidence": 0.95},
                        {"name": "人员", "count": 3, "confidence": 0.89},
                        {"name": "建筑物", "count": 1, "confidence": 0.97},
                        {"name": "交通标志", "count": 2, "confidence": 0.85}
                    ]
                }
            },
            {
                "type": VisionResultType.DOCUMENT_ANALYSIS,
                "content": "文档类型: 发票\n发票号码: INV2025001\n金额: ¥1,234.56\n开票日期: 2025-06-05",
                "confidence": 0.91,
                "details": {
                    "document_type": "invoice",
                    "fields_extracted": 4,
                    "currency": "CNY",
                    "amount": 1234.56
                }
            },
            {
                "type": VisionResultType.TEXT_RECOGNITION,
                "content": "产品名称: 智能手机\n型号: ABC-123\n序列号: SN123456789\n生产日期: 2025-05-15",
                "confidence": 0.87,
                "details": {
                    "detected_text_count": 4,
                    "language": "zh",
                    "document_type": "product_label"
                }
            },
            {
                "type": VisionResultType.FACE_RECOGNITION,
                "content": "检测到人脸: 1个\n年龄估计: 25-35岁\n性别: 男性\n表情: 微笑",
                "confidence": 0.83,
                "details": {
                    "face_count": 1,
                    "age_range": [25, 35],
                    "gender": "male",
                    "emotion": "smile",
                    "face_quality": "good"
                }
            }
        ]
    
    async def recognize(self, record_data: Dict[str, Any]) -> VisionResult:
        """
        模拟图片识别过程
        
        Args:
            record_data: 记录数据，包含图片信息
            
        Returns:
            VisionResult: 识别结果
        """
        # 模拟处理时间
        processing_time = random.uniform(0.5, 2.0)
        await asyncio.sleep(processing_time)
        
        # 根据输入数据选择合适的Mock结果
        mock_result = self._select_mock_result(record_data)
        
        # 添加一些随机性
        mock_result = self._add_randomness(mock_result)
        
        return VisionResult(
            type=mock_result["type"],
            content=mock_result["content"],
            confidence=mock_result["confidence"],
            details=mock_result["details"],
            processing_time=processing_time
        )
    
    def _select_mock_result(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """根据输入数据选择合适的Mock结果"""
        
        source_text = record_data.get("source_text", "").lower()
        
        # 根据源文本内容智能选择Mock结果
        if any(keyword in source_text for keyword in ["身份证", "id", "证件"]):
            return self.mock_results[0]  # 身份证识别
        elif any(keyword in source_text for keyword in ["合同", "contract", "协议"]):
            return self.mock_results[1]  # 合同识别
        elif any(keyword in source_text for keyword in ["车辆", "汽车", "交通", "监控"]):
            return self.mock_results[2]  # 物体检测
        elif any(keyword in source_text for keyword in ["发票", "invoice", "票据"]):
            return self.mock_results[3]  # 发票识别
        elif any(keyword in source_text for keyword in ["产品", "标签", "序列号"]):
            return self.mock_results[4]  # 产品标签
        elif any(keyword in source_text for keyword in ["人脸", "face", "人员"]):
            return self.mock_results[5]  # 人脸识别
        else:
            # 随机选择一个结果
            return random.choice(self.mock_results)
    
    def _add_randomness(self, mock_result: Dict[str, Any]) -> Dict[str, Any]:
        """为Mock结果添加随机性"""
        
        result = mock_result.copy()
        
        # 随机调整置信度 (±0.05)
        confidence_delta = random.uniform(-0.05, 0.05)
        result["confidence"] = max(0.1, min(1.0, result["confidence"] + confidence_delta))
        
        # 为某些类型添加随机变化
        if result["type"] == VisionResultType.TEXT_RECOGNITION:
            # 随机添加一些变化
            if random.random() < 0.3:  # 30%概率添加额外信息
                result["content"] += f"\n备注: 图片质量{'良好' if random.random() > 0.5 else '一般'}"
        
        elif result["type"] == VisionResultType.OBJECT_DETECTION:
            # 随机调整检测到的物体数量
            if "objects" in result["details"]:
                for obj in result["details"]["objects"]:
                    if random.random() < 0.2:  # 20%概率调整数量
                        obj["count"] = max(1, obj["count"] + random.randint(-1, 1))
        
        # 添加处理时间戳
        result["details"]["processed_at"] = datetime.now().isoformat()
        result["details"]["mock_version"] = "1.0.0"
        
        return result
    
    async def get_supported_types(self) -> list:
        """获取支持的识别类型"""
        return [result["type"] for result in self.mock_results]
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "provider": "mock",
            "supported_types": await self.get_supported_types(),
            "mock_results_count": len(self.mock_results),
            "version": "1.0.0"
        }

# 创建全局实例
mock_vision_provider = MockVisionProvider()
