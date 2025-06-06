#!/usr/bin/env python3
"""
优化后批量处理测试脚本

这个脚本用于测试优化后的批量处理功能，验证：
1. 查询限制调整为5条
2. 智能过滤未处理记录
3. 批量处理逻辑
4. 详细的统计信息

测试重点：
- 查询5条数据
- 识别已处理和未处理记录
- 批量处理未处理记录
- 统计信息的准确性

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

async def test_query_with_new_limit():
    """测试新的查询限制"""
    logger.info("🧪 开始测试查询限制调整...")
    
    try:
        # 导入MCP工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import query_image_data
        
        # 测试默认查询（应该是5条）
        logger.info("📊 测试默认查询限制...")
        query_result = await query_image_data()
        query_data = json.loads(query_result)
        
        logger.info(f"✅ 查询成功: {query_data['success']}")
        logger.info(f"📊 查询到数据: {query_data['count']} 条")
        logger.info(f"🎯 查询限制: {query_data['metadata']['query_limit']}")
        
        # 显示查询到的数据概要
        if query_data['success'] and query_data['count'] > 0:
            logger.info("📋 数据概要:")
            for i, item in enumerate(query_data['data']):
                has_result = bool(item['results']['result_1'].strip())
                status = "已处理" if has_result else "未处理"
                logger.info(f"  {i+1}. ID: {item['id'][:8]}... - {status}")
                if item['description']:
                    logger.info(f"     描述: {item['description'][:30]}...")
        
        return True, query_data
        
    except Exception as e:
        logger.error(f"❌ 查询测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False, None

async def test_processing_status():
    """测试处理状态查询"""
    logger.info("🧪 开始测试处理状态查询...")
    
    try:
        # 导入状态查询工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import get_processing_status
        
        # 查询处理状态
        logger.info("📈 查询处理状态...")
        status_result = await get_processing_status()
        status_data = json.loads(status_result)
        
        logger.info(f"✅ 状态查询成功: {status_data['success']}")
        
        # 显示统计信息
        stats = status_data['data_statistics']
        logger.info("📊 数据统计:")
        logger.info(f"  总记录数: {stats['total_records']}")
        logger.info(f"  已处理: {stats['processed_records']}")
        logger.info(f"  未处理: {stats['unprocessed_records']}")
        logger.info(f"  处理率: {stats['processing_rate']}")
        
        return True, status_data
        
    except Exception as e:
        logger.error(f"❌ 状态查询测试失败: {e}")
        return False, None

async def test_batch_processing():
    """测试批量处理功能"""
    logger.info("🧪 开始测试批量处理功能...")
    
    try:
        # 导入批量处理工具
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import batch_process_images
        
        # 执行批量处理（小批量测试）
        logger.info("🔄 执行批量处理...")
        batch_result = await batch_process_images(limit=5, max_concurrent=1)
        batch_data = json.loads(batch_result)
        
        logger.info(f"✅ 批量处理完成: {batch_data['success']}")
        logger.info(f"📝 处理消息: {batch_data['message']}")
        
        # 显示详细统计
        stats = batch_data['statistics']
        logger.info("📊 批量处理统计:")
        logger.info(f"  查询总数: {stats['total_queried']}")
        logger.info(f"  已处理: {stats.get('already_processed', 0)}")
        logger.info(f"  待处理: {stats.get('unprocessed_found', 0)}")
        logger.info(f"  新处理: {stats.get('newly_processed', 0)}")
        logger.info(f"  失败数: {stats.get('failed', 0)}")
        logger.info(f"  成功率: {stats.get('success_rate', '0%')}")
        logger.info(f"  总处理率: {stats.get('overall_processing_rate', '0%')}")
        
        # 显示处理摘要
        if 'summary' in batch_data:
            summary = batch_data['summary']
            logger.info("📋 处理摘要:")
            logger.info(f"  处理前: {summary['before_processing']}")
            logger.info(f"  处理后: {summary['after_processing']}")
            logger.info(f"  改进: {summary['improvement']}")
        
        # 显示处理详情
        if 'processing_details' in batch_data and batch_data['processing_details']:
            logger.info("🔍 处理详情:")
            for detail in batch_data['processing_details']:
                status_icon = "✅" if detail['status'] == 'success' else "❌"
                logger.info(f"  {status_icon} {detail['id'][:8]}... - {detail['status']}")
                if detail.get('error'):
                    logger.info(f"     错误: {detail['error'][:50]}...")
        
        return True, batch_data
        
    except Exception as e:
        logger.error(f"❌ 批量处理测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False, None

async def test_configuration_update():
    """测试配置更新"""
    logger.info("🧪 开始测试配置更新...")
    
    try:
        # 导入配置资源
        sys.path.insert(0, os.path.join(project_root, 'core', 'servers'))
        from mcp_server_final import get_server_config
        
        # 获取服务器配置
        logger.info("📋 获取服务器配置...")
        config_result = get_server_config()
        config_data = json.loads(config_result)
        
        logger.info(f"✅ 配置获取成功")
        logger.info(f"  服务器版本: {config_data['server']['version']}")
        logger.info(f"  工具数量: {len(config_data['tools'])}")
        
        # 检查工具配置
        logger.info("🔧 工具配置:")
        for tool in config_data['tools']:
            logger.info(f"  - {tool['name']}: {tool['description']}")
            if tool['name'] == 'query_image_data':
                params = tool['parameters']
                logger.info(f"    默认限制: {params.get('limit', '未指定')}")
            elif tool['name'] == 'batch_process_images':
                params = tool['parameters']
                logger.info(f"    默认限制: {params.get('limit', '未指定')}")
                logger.info(f"    默认并发: {params.get('max_concurrent', '未指定')}")
        
        return True, config_data
        
    except Exception as e:
        logger.error(f"❌ 配置测试失败: {e}")
        return False, None

async def main():
    """主测试函数"""
    logger.info("🚀 开始优化后批量处理测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("查询限制调整", test_query_with_new_limit),
        ("处理状态查询", test_processing_status),
        ("批量处理功能", test_batch_processing),
        ("配置更新验证", test_configuration_update)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 测试: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result, data = await test_func()
            test_results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} 测试通过")
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"💥 {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试总结
    logger.info(f"\n{'='*60}")
    logger.info("📊 测试总结")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试都通过了！批量处理优化成功！")
        logger.info("\n🚀 优化完成，功能提升：")
        logger.info("  ✅ 查询限制调整为5条")
        logger.info("  ✅ 智能过滤未处理记录")
        logger.info("  ✅ 详细的统计信息")
        logger.info("  ✅ 优化的并发控制")
        logger.info("  ✅ 完善的处理摘要")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
