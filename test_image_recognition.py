#!/usr/bin/env python3
"""
图像识别功能测试脚本

这个脚本用于测试新开发的图像识别功能，包括：
1. 简道云图片数据查询
2. 图片下载和验证
3. 通义千问Vision API调用
4. 识别结果更新

测试流程：
1. 测试简道云客户端的新方法
2. 测试图像处理器功能
3. 测试通义千问Vision客户端
4. 测试完整的识别流程

作者：MCP图像识别系统
版本：1.0.0
"""

import asyncio
import sys
import os
import logging

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'core', 'src')
sys.path.insert(0, src_path)

# 导入测试模块
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
from mcp_jiandaoyun.image_processor import ImageProcessor, QwenVisionClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_jiandaoyun_client():
    """测试简道云客户端的新功能"""
    logger.info("🧪 开始测试简道云客户端...")
    
    try:
        client = JianDaoYunClient()
        
        # 测试查询图片数据
        logger.info("📊 测试查询图片数据...")
        data_list = await client.query_image_data(limit=3)
        logger.info(f"✅ 查询成功，返回 {len(data_list)} 条数据")
        
        # 显示查询结果
        for i, item in enumerate(data_list):
            logger.info(f"📋 记录 {i+1}:")
            logger.info(f"  ID: {item.get('_id', 'N/A')}")
            logger.info(f"  创建时间: {item.get('createTime', 'N/A')}")
            
            # 检查附件字段
            attachment_field = client.attachment_field
            if attachment_field in item:
                attachment_data = item[attachment_field]
                if isinstance(attachment_data, dict) and 'value' in attachment_data:
                    attachment_value = attachment_data['value']
                    logger.info(f"  附件URL: {attachment_value}")
                else:
                    logger.info(f"  附件数据: {attachment_data}")
            else:
                logger.info(f"  附件字段 {attachment_field} 不存在")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 简道云客户端测试失败: {e}")
        return False

async def test_image_processor():
    """测试图像处理器功能"""
    logger.info("🧪 开始测试图像处理器...")
    
    try:
        processor = ImageProcessor()
        
        # 测试图片下载（使用一个小的测试图片）
        test_url = "https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg"
        logger.info(f"📥 测试图片下载: {test_url}")
        
        image_bytes = await processor.download_image(test_url)
        logger.info(f"✅ 图片下载成功，大小: {len(image_bytes)} 字节")
        
        # 测试图片验证
        logger.info("🔍 测试图片验证...")
        is_valid = processor.validate_image(image_bytes)
        logger.info(f"✅ 图片验证结果: {is_valid}")
        
        # 测试Base64转换
        logger.info("🔄 测试Base64转换...")
        image_base64 = processor.image_to_base64(image_bytes)
        logger.info(f"✅ Base64转换成功，长度: {len(image_base64)} 字符")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 图像处理器测试失败: {e}")
        return False

async def test_qwen_vision_client():
    """测试通义千问Vision客户端"""
    logger.info("🧪 开始测试通义千问Vision客户端...")
    
    try:
        client = QwenVisionClient()
        processor = ImageProcessor()
        
        # 下载测试图片
        test_url = "https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg"
        image_bytes = await processor.download_image(test_url)
        image_base64 = processor.image_to_base64(image_bytes)
        
        # 测试图像识别
        logger.info("🤖 测试图像识别...")
        results = await client.recognize_image(image_base64, "请描述这张图片的内容")
        logger.info("✅ 图像识别成功")
        
        # 显示识别结果
        for key, value in results.items():
            logger.info(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 通义千问Vision客户端测试失败: {e}")
        return False

async def test_complete_workflow():
    """测试完整的图像识别工作流程"""
    logger.info("🧪 开始测试完整工作流程...")
    
    try:
        # 初始化所有组件
        jiandaoyun_client = JianDaoYunClient()
        image_processor = ImageProcessor()
        qwen_client = QwenVisionClient()
        
        # 1. 查询图片数据
        logger.info("📊 步骤1: 查询图片数据...")
        data_list = await jiandaoyun_client.query_image_data(limit=1)
        
        if not data_list:
            logger.warning("⚠️ 没有找到图片数据，跳过完整流程测试")
            return True
        
        # 获取第一条记录
        record = data_list[0]
        data_id = record.get('_id')
        
        # 提取图片URL
        attachment_field = jiandaoyun_client.attachment_field
        image_url = ""
        if attachment_field in record:
            attachment_data = record[attachment_field]
            logger.info(f"🔍 附件数据类型: {type(attachment_data)}")
            logger.info(f"🔍 附件数据内容: {attachment_data}")

            if isinstance(attachment_data, dict) and 'value' in attachment_data:
                # 简道云返回格式：{"value": [{"url": "...", "name": "...", ...}]}
                attachment_value = attachment_data['value']
                if isinstance(attachment_value, list) and len(attachment_value) > 0:
                    first_attachment = attachment_value[0]
                    if isinstance(first_attachment, dict) and 'url' in first_attachment:
                        image_url = first_attachment['url']
                        logger.info(f"✅ 成功提取图片URL: {image_url}")
            elif isinstance(attachment_data, list) and len(attachment_data) > 0:
                # 直接是数组格式
                first_attachment = attachment_data[0]
                if isinstance(first_attachment, dict) and 'url' in first_attachment:
                    image_url = first_attachment['url']
                    logger.info(f"✅ 成功提取图片URL: {image_url}")
        
        if not image_url:
            logger.warning("⚠️ 记录中没有找到图片URL，跳过完整流程测试")
            return True
        
        logger.info(f"🆔 测试记录ID: {data_id}")
        logger.info(f"🔗 图片URL: {image_url}")
        
        # 2. 下载和验证图片
        logger.info("📥 步骤2: 下载图片...")
        image_bytes = await image_processor.download_image(image_url)
        
        logger.info("🔍 步骤3: 验证图片...")
        if not image_processor.validate_image(image_bytes):
            raise ValueError("图片验证失败")
        
        # 3. 转换格式
        logger.info("🔄 步骤4: 转换图片格式...")
        image_base64 = image_processor.image_to_base64(image_bytes)
        
        # 4. 图像识别
        logger.info("🤖 步骤5: 图像识别...")
        recognition_results = await qwen_client.recognize_image(
            image_base64, 
            "请详细描述这张图片的内容，包括设备类型、数量、外观特征、环境等信息。"
        )
        
        # 5. 更新结果
        logger.info("📡 步骤6: 更新识别结果...")
        update_result = await jiandaoyun_client.update_recognition_results(data_id, recognition_results)
        
        logger.info("🎉 完整工作流程测试成功！")
        logger.info(f"✅ 更新结果: {update_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 完整工作流程测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始图像识别功能测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("简道云客户端", test_jiandaoyun_client),
        ("图像处理器", test_image_processor),
        ("通义千问Vision客户端", test_qwen_vision_client),
        ("完整工作流程", test_complete_workflow)
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
        logger.info("🎉 所有测试都通过了！图像识别功能开发成功！")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
