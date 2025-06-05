"""
MCP图像识别系统 - 主应用程序

这是系统的主入口文件，负责：
1. 创建FastAPI应用实例
2. 配置中间件和路由
3. 管理应用生命周期
4. 提供健康检查和工具查询接口

系统架构：
- 严格遵循MCP协议，所有简道云操作都通过MCP服务器进行
- 使用本地Qwen3:1.7b模型进行AI处理
- 支持图像识别（当前使用Mock实现）
- 提供RESTful API接口

重要原则：
- 绝对不允许绕过MCP直接调用简道云API
- 详细记录所有操作过程
- 提供完整的错误处理和日志记录

作者：MCP图像识别系统
版本：1.0.0
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api_server.config.settings import settings, validate_settings, print_config_summary
from api_server.models.models import (
    ProcessRecordRequest, BatchProcessRequest, APIResponse, 
    HealthCheckResponse, ToolsResponse
)
from api_server.services.ai_processor import ai_processor_service
from api_server.services.mcp_client import mcp_client_service

# ==================== 应用生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    在应用启动和关闭时执行必要的初始化和清理工作。
    """
    # 启动时的初始化工作
    print("🚀 启动简道云AI处理服务...")
    
    try:
        # 验证配置
        validate_settings()
        print("✅ 配置验证通过")
        
        # 打印配置摘要
        print_config_summary()
        
        # 健康检查（尝试建立MCP连接）
        print("🔗 健康检查时尝试建立MCP连接...")
        health_result = await ai_processor_service.health_check()
        
        if health_result.get("overall_status") == "healthy":
            print("🔍 服务健康检查: healthy")
        else:
            print("🔍 服务健康检查: unhealthy")
            print("⚠️ 部分服务不健康，但继续启动...")
            for service_name, service_health in health_result.get("services", {}).items():
                if service_health.get("status") != "healthy":
                    error_msg = service_health.get("error", "未知错误")
                    print(f"   - {service_name}: {error_msg}")
        
        print("🎉 服务启动完成!")
        
        yield  # 应用运行期间
        
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        raise
    
    # 关闭时的清理工作
    print("🔚 正在关闭服务...")
    try:
        # 这里可以添加清理逻辑
        pass
    except Exception as e:
        print(f"⚠️ 服务关闭时出错: {e}")

# ==================== FastAPI应用创建 ====================

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== 中间件配置 ====================

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全局异常处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    
    捕获所有未处理的异常，返回统一的错误响应格式。
    """
    error_response = APIResponse(
        success=False,
        message="服务器内部错误",
        error=str(exc)
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

# ==================== API接口不需要密钥验证 ====================
# 注意：简道云API密钥仅用于MCP服务器调用简道云API，不用于验证客户端请求

# ==================== 核心API路由 ====================

@app.get("/", response_model=APIResponse)
async def root():
    """
    根路径接口
    
    返回系统基本信息。
    """
    return APIResponse(
        success=True,
        message=f"欢迎使用{settings.APP_NAME}",
        data={
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "docs": "/docs",
            "health": "/health"
        }
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查接口
    
    检查所有服务组件的健康状态，包括：
    - MCP服务器连接状态
    - AI模型服务状态
    - 图像识别服务状态
    """
    try:
        health_result = await ai_processor_service.health_check()
        
        return HealthCheckResponse(
            overall_status=health_result.get("overall_status", "unhealthy"),
            services=health_result.get("services", {}),
            model_info=health_result.get("model_info", {})
        )
    except Exception as e:
        return HealthCheckResponse(
            overall_status="unhealthy",
            services={"error": {"status": "unhealthy", "error": str(e)}},
            model_info={}
        )

@app.get("/api/tools", response_model=ToolsResponse)
async def get_tools():
    """
    获取MCP工具列表接口
    
    查询MCP服务器提供的所有工具，用于调试和验证MCP连接。
    """
    try:
        tools_result = await mcp_client_service.get_tools()
        
        if tools_result.get("success"):
            tools = tools_result.get("tools", [])
            return ToolsResponse(
                success=True,
                tools=tools,
                count=len(tools)
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"获取工具列表失败: {tools_result.get('error')}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")

@app.post("/api/process-record", response_model=APIResponse)
async def process_record(request: ProcessRecordRequest):
    """
    处理单个记录接口

    执行完整的AI处理流程：
    1. 通过MCP获取简道云数据
    2. 进行图像识别处理
    3. 使用AI模型处理识别结果
    4. 通过MCP保存处理结果到简道云

    Args:
        request: 处理请求参数
    """
    try:
        print(f"📥 收到处理请求: {request.record_id}")
        
        # 执行AI处理流程
        result = await ai_processor_service.process_record(
            record_id=request.record_id,
            force_reprocess=request.force_reprocess
        )
        
        if result.success:
            print(f"📤 处理完成: {request.record_id} - 成功")
            return APIResponse(
                success=True,
                message="记录处理成功",
                data=result.model_dump()
            )
        else:
            print(f"📤 处理完成: {request.record_id} - 失败")
            return APIResponse(
                success=False,
                message="记录处理失败",
                error=result.error_message,
                data=result.model_dump()
            )
            
    except Exception as e:
        print(f"❌ 处理请求异常: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/api/batch-process", response_model=APIResponse)
async def batch_process(request: BatchProcessRequest):
    """
    批量处理记录接口

    并发处理多个记录，控制并发数量以避免系统过载。

    Args:
        request: 批量处理请求参数
    """
    try:
        print(f"📥 收到批量处理请求: {len(request.record_ids)} 条记录")
        
        # 执行批量AI处理
        result = await ai_processor_service.batch_process(
            record_ids=request.record_ids
        )
        
        print(f"📤 批量处理完成: 成功 {result.get('success_count', 0)}, 失败 {result.get('failed_count', 0)}")
        
        return APIResponse(
            success=True,
            message=f"批量处理完成: 成功 {result.get('success_count', 0)}, 失败 {result.get('failed_count', 0)}",
            data=result
        )
        
    except Exception as e:
        print(f"❌ 批量处理请求异常: {e}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")

# ==================== 服务启动函数 ====================

def start_server():
    """
    启动服务器
    
    使用Uvicorn启动FastAPI应用。
    注意：禁用reload模式以确保MCP连接稳定性。
    """
    # 设置Windows兼容的事件循环策略
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("🔧 已设置Windows ProactorEventLoop策略")
    
    # 启动服务器（禁用reload模式以确保MCP连接稳定）
    uvicorn.run(
        "api_server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # 禁用reload模式，确保MCP连接稳定
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
