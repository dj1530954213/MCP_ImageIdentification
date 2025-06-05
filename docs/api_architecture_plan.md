# 🚀 API触发式MCP服务架构规划

## 📁 新的项目结构

```
MCP_ImageIdentification/
├── api_server/                    # 新增：API服务模块
│   ├── main.py                   # FastAPI主服务
│   ├── routers/                  # API路由
│   │   ├── __init__.py
│   │   ├── webhook.py           # 简道云Webhook接收
│   │   └── health.py            # 健康检查
│   ├── services/                 # 业务服务层
│   │   ├── __init__.py
│   │   ├── mcp_client.py        # MCP客户端封装
│   │   ├── ai_processor.py      # AI处理服务
│   │   └── vision_service.py    # 图片识别服务(接口)
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── request_models.py    # 请求模型
│   │   └── response_models.py   # 响应模型
│   ├── providers/                # 服务提供者
│   │   ├── __init__.py
│   │   ├── local_ai_provider.py # 本地AI提供者
│   │   └── vision_provider.py   # 图片识别提供者
│   ├── mock/                     # Mock服务
│   │   ├── __init__.py
│   │   └── mock_vision.py       # Mock图片识别
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py          # 配置文件
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logger.py            # 日志工具
│       └── exceptions.py        # 异常定义
├── core/                         # 现有：MCP服务器
├── examples/                     # 现有：示例代码
├── tests/                        # 现有：测试
│   └── api_tests/               # 新增：API测试
└── docs/                         # 现有：文档
    └── api_design.md            # 新增：API设计文档
```

## 🔧 核心组件设计

### 1. FastAPI主服务 (api_server/main.py)

```python
from fastapi import FastAPI
from api_server.routers import webhook, health
from api_server.config.settings import settings

app = FastAPI(
    title="简道云AI处理服务",
    description="基于MCP的API触发式AI处理服务",
    version="1.0.0"
)

# 注册路由
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.on_event("startup")
async def startup_event():
    # 初始化MCP客户端
    # 初始化AI模型
    pass
```

### 2. Webhook路由 (api_server/routers/webhook.py)

```python
from fastapi import APIRouter, HTTPException
from api_server.models.request_models import ProcessRecordRequest
from api_server.services.ai_processor import AIProcessorService

router = APIRouter()

@router.post("/process-record")
async def process_record(request: ProcessRecordRequest):
    """处理简道云记录的主要接口"""
    try:
        processor = AIProcessorService()
        result = await processor.process_record(request.record_id)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. AI处理服务 (api_server/services/ai_processor.py)

```python
class AIProcessorService:
    def __init__(self):
        self.mcp_client = MCPClientService()
        self.vision_service = VisionService()
        self.ai_provider = LocalAIProvider()
    
    async def process_record(self, record_id: str):
        """完整的记录处理流程"""
        # 1. 获取数据
        record_data = await self.mcp_client.get_record(record_id)
        
        # 2. 图片识别 (Mock)
        vision_result = await self.vision_service.recognize(record_data)
        
        # 3. AI处理
        ai_result = await self.ai_provider.process(vision_result)
        
        # 4. 回写数据
        update_result = await self.mcp_client.update_record(record_id, ai_result)
        
        return update_result
```

### 4. 图片识别服务接口 (api_server/services/vision_service.py)

```python
from abc import ABC, abstractmethod

class VisionServiceInterface(ABC):
    @abstractmethod
    async def recognize(self, image_data: dict) -> dict:
        """图片识别接口"""
        pass

class VisionService:
    def __init__(self):
        # 根据配置选择实现
        if settings.USE_MOCK_VISION:
            self.provider = MockVisionProvider()
        else:
            self.provider = RealVisionProvider()  # 后期实现
    
    async def recognize(self, record_data: dict) -> dict:
        return await self.provider.recognize(record_data)
```

### 5. Mock图片识别 (api_server/mock/mock_vision.py)

```python
import random
from datetime import datetime

class MockVisionProvider:
    async def recognize(self, record_data: dict) -> dict:
        """Mock图片识别结果"""
        
        # 模拟不同类型的识别结果
        mock_results = [
            {
                "type": "text_recognition",
                "content": "身份证号码: 123456789012345678",
                "confidence": 0.95
            },
            {
                "type": "object_detection", 
                "content": "检测到物体: 汽车, 人员, 建筑物",
                "confidence": 0.88
            },
            {
                "type": "document_analysis",
                "content": "文档类型: 合同, 页数: 3, 关键信息: 甲方乙方签署",
                "confidence": 0.92
            }
        ]
        
        # 随机选择一个结果
        result = random.choice(mock_results)
        
        return {
            "recognition_result": result,
            "processed_time": datetime.now().isoformat(),
            "source_field": record_data.get("source_text", ""),
            "mock_data": True
        }
```

## 🔄 MCP服务器扩展

### 新增MCP工具

需要在现有MCP服务器中添加新的工具：

```python
@mcp.tool()
async def query_specific_record(record_id: str) -> str:
    """查询指定ID的记录"""
    # 实现查询特定记录的逻辑
    pass

@mcp.tool()
async def update_record(record_id: str, updates: dict) -> str:
    """更新指定记录"""
    # 实现更新记录的逻辑
    pass

@mcp.tool()
async def get_image_data(record_id: str, image_field: str) -> str:
    """获取记录中的图片数据"""
    # 实现获取图片的逻辑
    pass
```

## 📊 数据流设计

### 请求模型

```python
class ProcessRecordRequest(BaseModel):
    record_id: str
    trigger_source: str = "webhook"
    priority: int = 1
    
class RecordData(BaseModel):
    id: str
    source_text: str
    result_text: str
    image_url: Optional[str] = None
    status: str
```

### 响应模型

```python
class ProcessResult(BaseModel):
    success: bool
    record_id: str
    original_text: str
    processed_text: str
    recognition_result: dict
    processing_time: float
    timestamp: datetime
```

## 🚀 实施步骤

### 阶段1: 基础框架搭建 (1天)

1. **创建API服务结构**
   ```bash
   mkdir -p api_server/{routers,services,models,providers,mock,config,utils}
   ```

2. **实现FastAPI基础框架**
   - main.py - 主服务
   - webhook.py - Webhook接收
   - health.py - 健康检查

3. **配置管理**
   - settings.py - 配置文件
   - 环境变量管理

### 阶段2: MCP集成 (1天)

1. **扩展MCP服务器**
   - 添加新的工具函数
   - 支持单记录查询和更新

2. **MCP客户端封装**
   - 创建MCPClientService
   - 封装常用操作

### 阶段3: Mock服务实现 (0.5天)

1. **Mock图片识别**
   - 实现MockVisionProvider
   - 提供多种Mock结果

2. **AI处理Mock**
   - 简单的文本处理逻辑
   - 格式化输出

### 阶段4: 业务流程整合 (0.5天)

1. **AIProcessorService**
   - 整合完整处理流程
   - 错误处理和日志

2. **端到端测试**
   - API接口测试
   - 完整流程验证

## 🔌 接口设计

### 主要API端点

```
POST /api/process-record
- 处理指定记录

GET /health/status  
- 服务健康检查

GET /health/mcp
- MCP连接状态检查

POST /api/batch-process
- 批量处理 (可选)
```

### Webhook格式

```json
{
  "record_id": "683ff873c9a6587f71b6b880",
  "trigger_source": "button_click",
  "timestamp": "2025-06-05T10:30:00Z"
}
```

## 🎯 后期扩展点

1. **图片识别替换**
   - 实现RealVisionProvider
   - 支持多种识别模型

2. **AI模型替换**
   - 支持不同的本地AI模型
   - 模型热切换

3. **性能优化**
   - 异步队列处理
   - 缓存机制

4. **监控和日志**
   - 详细的处理日志
   - 性能监控指标

## 💡 关键优势

1. **渐进式开发** - Mock先行，逐步替换
2. **接口标准化** - 便于后期替换实现
3. **模块化设计** - 各组件独立，易于测试
4. **复用现有资产** - 充分利用现有MCP服务器
5. **易于扩展** - 预留了各种扩展点
