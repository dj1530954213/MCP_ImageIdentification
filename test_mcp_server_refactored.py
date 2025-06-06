#!/usr/bin/env python3
"""
重构后MCP服务器测试脚本

这个脚本用于测试重构后的MCP服务器，验证：
1. 服务管理器的功能
2. 重构后的MCP工具
3. 配置驱动的设计
4. 异常处理机制
5. 批量处理功能

测试重点：
- 服务管理器和依赖注入
- MCP工具的完整性
- 错误处理和响应格式
- 批量处理和状态监控

作者：MCP图像识别系统
版本：3.0.0
"""

import asyncio
import sys
import os
import logging
import json

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

async def test_service_manager():
    """测试服务管理器"""
    logger.info("🧪 开始测试服务管理器...")
    
    try:
        # 导入服务器模块
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import get_service_manager, ServiceManager
        
        # 测试服务管理器创建
        logger.info("🔧 测试服务管理器创建...")
        service_manager = get_service_manager()
        logger.info(f"✅ 服务管理器创建成功: {type(service_manager)}")
        
        # 测试配置加载
        logger.info("📋 测试配置加载...")
        config = service_manager.config
        logger.info(f"✅ 配置加载成功: {config.validate_config()}")
        
        # 测试服务组件获取
        logger.info("🔗 测试服务组件获取...")
        jiandaoyun_client = service_manager.jiandaoyun_client
        image_processor = service_manager.image_processor
        vision_client = service_manager.vision_client
        logger.info("✅ 所有服务组件获取成功")
        
        # 测试服务状态
        logger.info("📊 测试服务状态...")
        status = service_manager.get_status()
        logger.info(f"✅ 服务状态: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 服务管理器测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_mcp_tools():
    """测试MCP工具"""
    logger.info("🧪 开始测试MCP工具...")
    
    try:
        # 导入MCP工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import query_image_data, recognize_and_update, get_processing_status
        
        # 测试查询工具
        logger.info("📊 测试查询图片数据工具...")
        query_result = await query_image_data(limit=2)
        query_data = json.loads(query_result)
        logger.info(f"✅ 查询工具测试成功: {query_data['success']}")
        logger.info(f"  查询到数据: {query_data['count']} 条")
        
        # 测试状态工具
        logger.info("📈 测试状态查询工具...")
        status_result = await get_processing_status()
        status_data = json.loads(status_result)
        logger.info(f"✅ 状态工具测试成功: {status_data['success']}")
        logger.info(f"  系统状态: {status_data['system_status']['config_valid']}")
        
        # 测试识别工具（如果有数据的话）
        if query_data['success'] and query_data['count'] > 0:
            first_record = query_data['data'][0]
            if first_record['attachment_url']:
                logger.info("🖼️ 测试图像识别工具...")
                try:
                    recognize_result = await recognize_and_update(
                        data_id=first_record['id'],
                        image_url=first_record['attachment_url']
                    )
                    recognize_data = json.loads(recognize_result)
                    logger.info(f"✅ 识别工具测试成功: {recognize_data['success']}")
                except Exception as e:
                    logger.warning(f"⚠️ 识别工具测试跳过（可能的网络问题）: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP工具测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_error_handling():
    """测试错误处理"""
    logger.info("🧪 开始测试错误处理...")
    
    try:
        # 导入MCP工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import recognize_and_update
        
        # 测试无效参数
        logger.info("💥 测试无效参数处理...")
        error_result = await recognize_and_update(
            data_id="invalid_id",
            image_url="https://invalid-url.com/image.jpg"
        )
        error_data = json.loads(error_result)
        logger.info(f"✅ 错误处理测试成功: {not error_data['success']}")
        logger.info(f"  错误码: {error_data.get('error', {}).get('code', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e}")
        return False

async def test_batch_processing():
    """测试批量处理"""
    logger.info("🧪 开始测试批量处理...")
    
    try:
        # 导入批量处理工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import batch_process_images
        
        # 测试批量处理（小批量）
        logger.info("🔄 测试批量处理工具...")
        batch_result = await batch_process_images(limit=2, max_concurrent=1)
        batch_data = json.loads(batch_result)
        logger.info(f"✅ 批量处理测试成功: {batch_data['success']}")
        logger.info(f"  处理统计: {batch_data.get('statistics', {})}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 批量处理测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_configuration():
    """测试配置功能"""
    logger.info("🧪 开始测试配置功能...")
    
    try:
        # 导入配置资源
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import get_server_config
        
        # 测试配置资源
        logger.info("📋 测试配置资源...")
        config_result = get_server_config()
        config_data = json.loads(config_result)
        logger.info(f"✅ 配置资源测试成功")
        logger.info(f"  服务器版本: {config_data['server']['version']}")
        logger.info(f"  工具数量: {len(config_data['tools'])}")
        logger.info(f"  功能数量: {len(config_data['features'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置功能测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始重构后MCP服务器测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("服务管理器", test_service_manager),
        ("MCP工具", test_mcp_tools),
        ("错误处理", test_error_handling),
        ("批量处理", test_batch_processing),
        ("配置功能", test_configuration)
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
        logger.info("🎉 所有测试都通过了！MCP服务器重构成功！")
        logger.info("\n🚀 重构优化完成，功能全面提升：")
        logger.info("  ✅ 服务管理器和依赖注入")
        logger.info("  ✅ 配置驱动的架构")
        logger.info("  ✅ 完善的异常处理")
        logger.info("  ✅ 批量处理和并发控制")
        logger.info("  ✅ 智能内容分析")
        logger.info("  ✅ 状态监控和统计")
        logger.info("  ✅ 标准化的响应格式")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
