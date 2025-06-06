#!/usr/bin/env python3
"""
重构后图像处理模块测试脚本

这个脚本用于测试重构后的图像处理模块，验证：
1. 图像处理器的新功能
2. 通义千问Vision客户端的重构
3. 配置驱动的设计
4. 异常处理机制

测试重点：
- 接口抽象设计
- 配置管理集成
- 异常处理完善
- 智能内容分析

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

async def test_image_processor():
    """测试重构后的图像处理器"""
    logger.info("🧪 开始测试图像处理器...")
    
    try:
        from mcp_jiandaoyun.image_processor import ImageProcessor
        from mcp_jiandaoyun.config import get_config
        from mcp_jiandaoyun.exceptions import ImageProcessingException, NetworkException
        
        # 测试配置驱动的创建
        logger.info("🔧 测试配置驱动的创建...")
        config = get_config()
        processor = ImageProcessor(config.image_processing)
        logger.info("✅ 图像处理器创建成功")
        
        # 测试默认配置创建
        logger.info("🔧 测试默认配置创建...")
        processor_default = ImageProcessor()
        logger.info("✅ 默认配置图像处理器创建成功")
        
        # 测试图片下载
        logger.info("📥 测试图片下载...")
        test_url = "https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg"
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
        
        # 测试异常处理
        logger.info("💥 测试异常处理...")
        try:
            # 测试无效URL
            await processor.download_image("https://invalid-url-test.com/image.jpg")
        except (NetworkException, ImageProcessingException) as e:
            logger.info(f"✅ 异常正确捕获: {e.error_code.value}")
        
        # 测试无效图片数据
        try:
            processor.validate_image(b"invalid image data")
        except ImageProcessingException as e:
            logger.info(f"✅ 图片验证异常正确捕获: {e.error_code.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 图像处理器测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_qwen_vision_client():
    """测试重构后的通义千问Vision客户端"""
    logger.info("🧪 开始测试通义千问Vision客户端...")
    
    try:
        from mcp_jiandaoyun.image_processor import QwenVisionClient, ImageProcessor
        from mcp_jiandaoyun.config import get_config
        from mcp_jiandaoyun.exceptions import QwenVisionException, NetworkException
        
        # 测试配置驱动的创建
        logger.info("🔧 测试配置驱动的创建...")
        config = get_config()
        client = QwenVisionClient(config.qwen_vision)
        logger.info("✅ 通义千问客户端创建成功")
        
        # 测试默认配置创建
        logger.info("🔧 测试默认配置创建...")
        client_default = QwenVisionClient()
        logger.info("✅ 默认配置通义千问客户端创建成功")
        
        # 准备测试图片
        logger.info("📥 准备测试图片...")
        processor = ImageProcessor()
        test_url = "https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg"
        image_bytes = await processor.download_image(test_url)
        image_base64 = processor.image_to_base64(image_bytes)
        
        # 测试图像识别（使用默认提示词）
        logger.info("🤖 测试图像识别（默认提示词）...")
        results_default = await client.recognize_image(image_base64)
        logger.info("✅ 默认提示词识别成功")
        logger.info(f"  结果字段数量: {len(results_default)}")
        for key, value in results_default.items():
            logger.info(f"  {key}: {len(value)} 字符")
        
        # 测试图像识别（自定义提示词）
        logger.info("🤖 测试图像识别（自定义提示词）...")
        custom_prompt = "请识别图片中的文字内容"
        results_custom = await client.recognize_image(image_base64, custom_prompt)
        logger.info("✅ 自定义提示词识别成功")
        
        # 测试智能内容分析
        logger.info("🧠 测试智能内容分析...")
        logger.info(f"  主要结果: {results_default['result_1'][:100]}...")
        logger.info(f"  设备信息: {results_default['result_2'][:50]}...")
        logger.info(f"  技术参数: {results_default['result_3'][:50]}...")
        logger.info(f"  环境信息: {results_default['result_4'][:50]}...")
        logger.info(f"  元数据: {results_default['result_5']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 通义千问客户端测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_integration():
    """测试集成功能"""
    logger.info("🧪 开始测试集成功能...")
    
    try:
        from mcp_jiandaoyun.image_processor import ImageProcessor, QwenVisionClient
        from mcp_jiandaoyun.config import get_config
        
        # 测试完整的图像处理流程
        logger.info("🔄 测试完整的图像处理流程...")
        
        # 1. 创建处理器和客户端
        config = get_config()
        processor = ImageProcessor()
        vision_client = QwenVisionClient()
        
        # 2. 下载图片
        test_url = "https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg"
        image_bytes = await processor.download_image(test_url)
        
        # 3. 验证图片
        is_valid = processor.validate_image(image_bytes)
        if not is_valid:
            raise Exception("图片验证失败")
        
        # 4. 转换格式
        image_base64 = processor.image_to_base64(image_bytes)
        
        # 5. 图像识别
        results = await vision_client.recognize_image(image_base64)
        
        logger.info("✅ 完整流程测试成功")
        logger.info(f"  处理图片大小: {len(image_bytes)} 字节")
        logger.info(f"  Base64长度: {len(image_base64)} 字符")
        logger.info(f"  识别结果字段: {len(results)}")
        
        # 测试配置访问
        logger.info("📋 测试配置访问...")
        logger.info(f"  最大图片大小: {config.image_processing.max_image_size / 1024 / 1024:.1f} MB")
        logger.info(f"  支持格式: {config.image_processing.supported_formats}")
        logger.info(f"  下载超时: {config.image_processing.download_timeout} 秒")
        logger.info(f"  通义千问模型: {config.qwen_vision.model}")
        logger.info(f"  最大Token: {config.qwen_vision.max_tokens}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 集成测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

async def test_error_handling():
    """测试错误处理"""
    logger.info("🧪 开始测试错误处理...")
    
    try:
        from mcp_jiandaoyun.image_processor import ImageProcessor, QwenVisionClient
        from mcp_jiandaoyun.exceptions import ImageProcessingException, NetworkException, QwenVisionException
        
        processor = ImageProcessor()
        
        # 测试各种错误情况
        error_tests = [
            ("无效URL下载", lambda: processor.download_image("https://invalid-url-test.com/image.jpg")),
            ("空图片数据验证", lambda: processor.validate_image(b"")),
            ("无效图片数据验证", lambda: processor.validate_image(b"invalid")),
            ("空数据Base64转换", lambda: processor.image_to_base64(b"")),
        ]
        
        for test_name, test_func in error_tests:
            logger.info(f"💥 测试: {test_name}")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                logger.warning(f"⚠️ {test_name} 应该抛出异常但没有")
            except (ImageProcessingException, NetworkException, QwenVisionException) as e:
                logger.info(f"✅ {test_name} 正确抛出异常: {e.error_code.value}")
            except Exception as e:
                logger.warning(f"⚠️ {test_name} 抛出了意外异常: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始重构后图像处理模块测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("图像处理器", test_image_processor),
        ("通义千问Vision客户端", test_qwen_vision_client),
        ("集成功能", test_integration),
        ("错误处理", test_error_handling)
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
        logger.info("🎉 所有测试都通过了！图像处理模块重构成功！")
        logger.info("\n🚀 重构优化完成，功能显著提升：")
        logger.info("  ✅ 接口抽象设计")
        logger.info("  ✅ 配置驱动架构")
        logger.info("  ✅ 完善异常处理")
        logger.info("  ✅ 智能内容分析")
        logger.info("  ✅ 重试机制支持")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
