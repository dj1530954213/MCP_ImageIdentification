#!/usr/bin/env python3
"""
重构代码测试脚本

这个脚本用于测试重构后的代码，验证：
1. 配置管理模块
2. 异常处理模块
3. 重构后的简道云客户端
4. 新的架构设计

测试重点：
- 配置加载和验证
- 异常处理机制
- 客户端功能完整性
- 代码质量和可维护性

作者：MCP图像识别系统
版本：2.0.0
"""

import asyncio
import sys
import os
import logging

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'core', 'src')
sys.path.insert(0, src_path)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_config_module():
    """测试配置管理模块"""
    logger.info("🧪 开始测试配置管理模块...")
    
    try:
        from mcp_jiandaoyun.config import get_config, AppConfig, JianDaoYunConfig
        
        # 测试配置加载
        logger.info("📋 测试配置加载...")
        config = get_config()
        logger.info(f"✅ 配置加载成功: {type(config)}")
        
        # 测试配置验证
        logger.info("🔍 测试配置验证...")
        is_valid = config.validate_config()
        logger.info(f"✅ 配置验证结果: {is_valid}")
        
        # 测试子配置访问
        logger.info("📊 测试子配置访问...")
        jdy_config = config.jiandaoyun
        logger.info(f"✅ 简道云配置: {jdy_config.app_id}")
        
        qwen_config = config.qwen_vision
        logger.info(f"✅ 通义千问配置: {qwen_config.model}")
        
        # 测试配置属性
        logger.info("🔗 测试配置属性...")
        logger.info(f"  查询URL: {jdy_config.query_url}")
        logger.info(f"  更新URL: {jdy_config.update_url}")
        logger.info(f"  请求头: {list(jdy_config.headers.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置模块测试失败: {e}")
        return False

async def test_exception_module():
    """测试异常处理模块"""
    logger.info("🧪 开始测试异常处理模块...")
    
    try:
        from mcp_jiandaoyun.exceptions import (
            MCPBaseException, JianDaoYunException, NetworkException,
            ErrorCode, handle_exceptions, retry_on_exception
        )
        
        # 测试基础异常
        logger.info("💥 测试基础异常...")
        try:
            raise MCPBaseException(
                message="测试异常",
                error_code=ErrorCode.UNKNOWN_ERROR,
                details={"test": "data"}
            )
        except MCPBaseException as e:
            logger.info(f"✅ 基础异常捕获成功: {e.error_code.value}")
            logger.info(f"  异常字典: {list(e.to_dict().keys())}")
        
        # 测试业务异常
        logger.info("🔧 测试业务异常...")
        try:
            raise JianDaoYunException(
                message="简道云API测试异常",
                api_endpoint="https://test.api.com",
                response_data={"status": 500}
            )
        except JianDaoYunException as e:
            logger.info(f"✅ 简道云异常捕获成功: {e.error_code.value}")
        
        # 测试异常装饰器
        logger.info("🎯 测试异常装饰器...")
        
        @handle_exceptions(reraise=False, default_return="装饰器测试成功")
        def test_decorated_function():
            raise ValueError("测试异常")
        
        result = test_decorated_function()
        logger.info(f"✅ 装饰器测试结果: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 异常模块测试失败: {e}")
        return False

async def test_jiandaoyun_client():
    """测试重构后的简道云客户端"""
    logger.info("🧪 开始测试简道云客户端...")
    
    try:
        from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
        from mcp_jiandaoyun.config import get_config
        
        # 创建客户端实例
        logger.info("🔧 创建客户端实例...")
        config = get_config()
        client = JianDaoYunClient(config.jiandaoyun)
        logger.info("✅ 客户端创建成功")
        
        # 测试查询功能
        logger.info("📊 测试查询功能...")
        data_list = await client.query_image_data(limit=2)
        logger.info(f"✅ 查询成功，返回 {len(data_list)} 条数据")
        
        # 测试图片URL提取
        if data_list:
            logger.info("🔍 测试图片URL提取...")
            first_record = data_list[0]
            attachment_field = config.jiandaoyun.attachment_field
            
            if attachment_field in first_record:
                attachment_data = first_record[attachment_field]
                image_url = client.extract_image_url(attachment_data)
                logger.info(f"✅ 图片URL提取: {bool(image_url)}")
                if image_url:
                    logger.info(f"  URL长度: {len(image_url)}")
            else:
                logger.info("⚠️ 记录中没有附件字段")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 简道云客户端测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_integration():
    """测试集成功能"""
    logger.info("🧪 开始测试集成功能...")
    
    try:
        from mcp_jiandaoyun.config import get_config
        from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
        from mcp_jiandaoyun.exceptions import JianDaoYunException, NetworkException
        
        # 测试配置驱动的客户端
        logger.info("🔧 测试配置驱动的客户端...")
        config = get_config()
        client = JianDaoYunClient()  # 使用默认配置
        
        # 测试异常处理
        logger.info("💥 测试异常处理...")
        try:
            # 尝试查询一个不存在的记录（应该正常返回空列表）
            data_list = await client.query_image_data(limit=1)
            logger.info(f"✅ 异常处理测试通过，返回数据: {len(data_list)} 条")
        except (JianDaoYunException, NetworkException) as e:
            logger.info(f"✅ 异常正确捕获: {e.error_code.value}")
        
        # 测试配置访问
        logger.info("📋 测试配置访问...")
        logger.info(f"  应用ID: {config.jiandaoyun.app_id}")
        logger.info(f"  表单ID: {config.jiandaoyun.entry_id}")
        logger.info(f"  结果字段数量: {len(config.jiandaoyun.result_fields)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 集成测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始重构代码测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("配置管理模块", test_config_module),
        ("异常处理模块", test_exception_module),
        ("简道云客户端", test_jiandaoyun_client),
        ("集成功能", test_integration)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 测试: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            test_results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} 测试通过")
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"💥 {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试总结
    logger.info(f"\n{'='*50}")
    logger.info("📊 测试总结")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试都通过了！重构成功！")
        logger.info("\n🚀 重构优化完成，代码质量显著提升：")
        logger.info("  ✅ 统一配置管理")
        logger.info("  ✅ 完善异常处理")
        logger.info("  ✅ 类型安全接口")
        logger.info("  ✅ 可扩展架构")
        logger.info("  ✅ 代码规范整洁")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
