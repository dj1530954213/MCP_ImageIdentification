"""
MCP图像识别系统 - 数据模型定义

这个模块定义了系统中使用的所有数据模型，包括：
1. API请求和响应模型
2. 图像识别结果模型
3. AI处理结果模型
4. 处理状态枚举

所有模型都使用Pydantic进行数据验证和序列化，
确保数据的类型安全和一致性。

作者：MCP图像识别系统
版本：1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# ==================== 枚举定义 ====================

class ProcessStatus(str, Enum):
    """
    处理状态枚举
    
    定义了记录处理的各种状态，用于跟踪处理进度。
    """
    PENDING = "pending"       # 等待处理
    PROCESSING = "processing" # 正在处理
    SUCCESS = "success"       # 处理成功
    FAILED = "failed"         # 处理失败
    CANCELLED = "cancelled"   # 处理取消

class VisionResultType(str, Enum):
    """
    图像识别结果类型枚举
    
    定义了支持的图像识别类型，当前使用Mock实现。
    """
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"     # 文档分析
    FACE_RECOGNITION = "FACE_RECOGNITION"       # 人脸识别
    OBJECT_DETECTION = "OBJECT_DETECTION"       # 物体检测
    TEXT_RECOGNITION = "TEXT_RECOGNITION"       # 文字识别
    SCENE_ANALYSIS = "SCENE_ANALYSIS"           # 场景分析

# ==================== API请求模型 ====================

class ProcessRecordRequest(BaseModel):
    """
    处理记录请求模型
    
    定义了处理单个记录时需要的参数。
    """
    record_id: str = Field(..., description="记录ID，用于标识要处理的记录")
    trigger_source: Optional[str] = Field("api", description="触发源，标识请求来源")
    priority: Optional[int] = Field(1, ge=1, le=10, description="处理优先级，1-10，数字越大优先级越高")
    force_reprocess: Optional[bool] = Field(False, description="是否强制重新处理")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "record_id": "test_record_001",
                "trigger_source": "postman_test",
                "priority": 1,
                "force_reprocess": True
            }
        }

class BatchProcessRequest(BaseModel):
    """
    批量处理请求模型
    
    定义了批量处理多个记录时需要的参数。
    """
    record_ids: List[str] = Field(..., description="要处理的记录ID列表")
    priority: Optional[int] = Field(1, ge=1, le=10, description="处理优先级")
    force_reprocess: Optional[bool] = Field(False, description="是否强制重新处理")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "record_ids": ["record_001", "record_002", "record_003"],
                "priority": 2,
                "force_reprocess": False
            }
        }

# ==================== 图像识别结果模型 ====================

class VisionResult(BaseModel):
    """
    图像识别结果模型
    
    封装图像识别的结果数据，包括识别类型、内容、置信度等。
    """
    type: VisionResultType = Field(..., description="识别类型")
    content: str = Field(..., description="识别内容的文本描述")
    confidence: float = Field(..., ge=0.0, le=1.0, description="识别置信度，0-1之间")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细识别结果")
    processing_time: float = Field(..., ge=0.0, description="处理耗时（秒）")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "type": "FACE_RECOGNITION",
                "content": "检测到1个面部，年龄25-35岁，男性，微笑",
                "confidence": 0.89,
                "details": {
                    "face_count": 1,
                    "age_range": "25-35",
                    "gender": "male",
                    "emotion": "smile"
                },
                "processing_time": 0.15
            }
        }

# ==================== AI处理结果模型 ====================

class AIProcessResult(BaseModel):
    """
    AI处理结果模型
    
    封装AI模型处理的结果数据，包括原始文本、处理后文本、分析结果等。
    """
    original_text: str = Field(..., description="原始输入文本")
    processed_text: str = Field(..., description="AI处理后的文本")
    ai_analysis: str = Field(..., description="AI分析结果")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI处理置信度")
    processing_time: float = Field(..., ge=0.0, description="AI处理耗时（秒）")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "original_text": "原始图像识别文本",
                "processed_text": "[AI识别] 处理后的结构化文本",
                "ai_analysis": "AI模型分析和处理的详细说明",
                "confidence": 0.85,
                "processing_time": 2.3
            }
        }

# ==================== 完整处理结果模型 ====================

class ProcessResult(BaseModel):
    """
    完整处理结果模型
    
    封装整个处理流程的结果，包括成功状态、各阶段结果、错误信息等。
    """
    success: bool = Field(..., description="处理是否成功")
    record_id: str = Field(..., description="处理的记录ID")
    status: ProcessStatus = Field(..., description="处理状态")
    vision_result: Optional[VisionResult] = Field(None, description="图像识别结果")
    ai_result: Optional[AIProcessResult] = Field(None, description="AI处理结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    processing_time: float = Field(..., ge=0.0, description="总处理耗时（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="处理时间戳")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "success": True,
                "record_id": "test_record_001",
                "status": "success",
                "vision_result": {
                    "type": "FACE_RECOGNITION",
                    "content": "检测到1个面部",
                    "confidence": 0.89,
                    "details": {},
                    "processing_time": 0.15
                },
                "ai_result": {
                    "original_text": "原始文本",
                    "processed_text": "[AI识别] 处理后文本",
                    "ai_analysis": "AI分析结果",
                    "confidence": 0.85,
                    "processing_time": 2.3
                },
                "error_message": None,
                "processing_time": 5.2,
                "timestamp": "2025-06-05T10:30:00"
            }
        }

# ==================== API响应模型 ====================

class APIResponse(BaseModel):
    """
    标准API响应模型
    
    定义了所有API接口的标准响应格式。
    """
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": {"result": "处理结果"},
                "error": None,
                "timestamp": "2025-06-05T10:30:00"
            }
        }

class HealthCheckResponse(BaseModel):
    """
    健康检查响应模型
    
    定义了健康检查接口的响应格式。
    """
    overall_status: str = Field(..., description="整体健康状态")
    services: Dict[str, Any] = Field(..., description="各服务的健康状态")
    model_info: Dict[str, Any] = Field(..., description="模型信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间戳")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "overall_status": "healthy",
                "services": {
                    "mcp": {"status": "healthy", "connected": True},
                    "ai": {"status": "healthy", "model": "qwen3:1.7b"},
                    "vision": {"status": "healthy", "type": "mock"}
                },
                "model_info": {
                    "ai_model": "qwen3:1.7b",
                    "vision_provider": "mock",
                    "use_local_ai": True
                },
                "timestamp": "2025-06-05T10:30:00"
            }
        }

class ToolsResponse(BaseModel):
    """
    工具列表响应模型
    
    定义了MCP工具列表接口的响应格式。
    """
    success: bool = Field(..., description="操作是否成功")
    tools: List[Dict[str, str]] = Field(..., description="MCP工具列表")
    count: int = Field(..., description="工具数量")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "success": True,
                "tools": [
                    {"name": "query_data", "description": "查询简道云数据"},
                    {"name": "process_and_save", "description": "处理文本并保存到简道云"}
                ],
                "count": 2,
                "timestamp": "2025-06-05T10:30:00"
            }
        }
