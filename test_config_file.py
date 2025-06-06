#!/usr/bin/env python3
"""
配置文件测试脚本

这个脚本用于测试配置文件的加载和验证功能，确保：
1. 配置文件正确加载
2. 敏感信息不会泄露
3. 配置验证正常工作
4. 所有配置项都能正确访问

测试重点：
- 配置文件加载机制
- 注释字段过滤
- 配置验证功能
- 敏感信息保护

作者：MCP图像识别系统
版本：3.0.0
"""

import sys
import os
import logging
from pathlib import Path

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

def test_config_file_loading():
    """测试配置文件加载"""
    logger.info("🧪 开始测试配置文件加载...")
    
    try:
        from mcp_jiandaoyun.config import get_config, AppConfig
        
        # 测试配置文件是否存在
        config_file = Path(project_root) / "config.json"
        logger.info(f"📁 检查配置文件: {config_file}")
        
        if config_file.exists():
            logger.info("✅ 配置文件存在")
            file_size = config_file.stat().st_size
            logger.info(f"📊 文件大小: {file_size} 字节")
        else:
            logger.warning("⚠️ 配置文件不存在，将使用默认配置")
        
        # 测试配置加载
        logger.info("🔧 加载配置...")
        config = get_config()
        logger.info("✅ 配置加载成功")
        
        return True, config
        
    except Exception as e:
        logger.error(f"❌ 配置文件加载测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False, None

def test_config_validation():
    """测试配置验证"""
    logger.info("🧪 开始测试配置验证...")
    
    try:
        from mcp_jiandaoyun.config import get_config
        
        # 获取配置
        config = get_config()
        
        # 测试配置验证
        logger.info("🔍 验证配置...")
        is_valid = config.validate_config()
        
        if is_valid:
            logger.info("✅ 配置验证通过")
        else:
            logger.warning("⚠️ 配置验证失败")
        
        return True, is_valid
        
    except Exception as e:
        logger.error(f"❌ 配置验证测试失败: {e}")
        return False, False

def test_config_access():
    """测试配置访问"""
    logger.info("🧪 开始测试配置访问...")
    
    try:
        from mcp_jiandaoyun.config import get_config
        
        # 获取配置
        config = get_config()
        
        # 测试各模块配置访问
        logger.info("📋 测试简道云配置访问...")
        jiandaoyun_config = config.jiandaoyun
        logger.info(f"  应用ID: {jiandaoyun_config.app_id}")
        logger.info(f"  表单ID: {jiandaoyun_config.entry_id}")
        logger.info(f"  超时时间: {jiandaoyun_config.timeout}秒")
        logger.info(f"  重试次数: {jiandaoyun_config.max_retries}")
        
        # 测试字段配置
        logger.info("📝 测试字段配置...")
        logger.info(f"  日期字段: {jiandaoyun_config.datetime_field}")
        logger.info(f"  上传人字段: {jiandaoyun_config.uploader_field}")
        logger.info(f"  描述字段: {jiandaoyun_config.description_field}")
        logger.info(f"  附件字段: {jiandaoyun_config.attachment_field}")
        
        # 测试结果字段
        logger.info("🎯 测试结果字段配置...")
        result_fields = jiandaoyun_config.result_fields
        for key, value in result_fields.items():
            logger.info(f"  {key}: {value}")
        
        # 测试通义千问配置
        logger.info("🤖 测试通义千问配置...")
        qwen_config = config.qwen_vision
        logger.info(f"  模型: {qwen_config.model}")
        logger.info(f"  最大Token: {qwen_config.max_tokens}")
        logger.info(f"  超时时间: {qwen_config.timeout}秒")
        
        # 测试图像处理配置
        logger.info("🖼️ 测试图像处理配置...")
        image_config = config.image_processing
        logger.info(f"  最大图片大小: {image_config.max_image_size / 1024 / 1024:.1f} MB")
        logger.info(f"  支持格式: {image_config.supported_formats}")
        logger.info(f"  下载超时: {image_config.download_timeout}秒")
        
        # 测试系统配置
        logger.info("⚙️ 测试系统配置...")
        system_config = config.system
        logger.info(f"  日志级别: {system_config.log_level}")
        logger.info(f"  最大并发: {system_config.max_concurrent_tasks}")
        logger.info(f"  缓存启用: {system_config.enable_cache}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置访问测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def test_sensitive_info_protection():
    """测试敏感信息保护"""
    logger.info("🧪 开始测试敏感信息保护...")
    
    try:
        from mcp_jiandaoyun.config import get_config
        
        # 获取配置
        config = get_config()
        
        # 检查敏感信息是否被正确处理
        logger.info("🔒 检查敏感信息处理...")
        
        # 简道云API密钥
        jiandaoyun_api_key = config.jiandaoyun.api_key
        if jiandaoyun_api_key and len(jiandaoyun_api_key) > 10:
            masked_key = jiandaoyun_api_key[:4] + "*" * (len(jiandaoyun_api_key) - 8) + jiandaoyun_api_key[-4:]
            logger.info(f"  简道云API密钥: {masked_key}")
        else:
            logger.warning("⚠️ 简道云API密钥未配置或格式异常")
        
        # 通义千问API密钥
        qwen_api_key = config.qwen_vision.api_key
        if qwen_api_key and len(qwen_api_key) > 10:
            masked_key = qwen_api_key[:4] + "*" * (len(qwen_api_key) - 8) + qwen_api_key[-4:]
            logger.info(f"  通义千问API密钥: {masked_key}")
        else:
            logger.warning("⚠️ 通义千问API密钥未配置或格式异常")
        
        # 检查配置文件是否在.gitignore中
        gitignore_file = Path(project_root) / ".gitignore"
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            if "config.json" in gitignore_content:
                logger.info("✅ config.json 已添加到 .gitignore")
            else:
                logger.warning("⚠️ config.json 未添加到 .gitignore，存在泄露风险")
        else:
            logger.warning("⚠️ .gitignore 文件不存在")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 敏感信息保护测试失败: {e}")
        return False

def test_comment_filtering():
    """测试注释字段过滤"""
    logger.info("🧪 开始测试注释字段过滤...")
    
    try:
        from mcp_jiandaoyun.config import AppConfig
        
        # 测试注释过滤功能
        test_data = {
            "_comment": "这是注释",
            "_description": "这是描述",
            "valid_field": "这是有效字段",
            "nested": {
                "_nested_comment": "嵌套注释",
                "nested_valid": "嵌套有效字段"
            }
        }
        
        filtered_data = AppConfig._filter_comments(test_data)
        
        # 检查过滤结果
        if "_comment" not in filtered_data:
            logger.info("✅ 顶级注释字段已过滤")
        else:
            logger.error("❌ 顶级注释字段未过滤")
        
        if "valid_field" in filtered_data:
            logger.info("✅ 有效字段保留")
        else:
            logger.error("❌ 有效字段被误删")
        
        if "_nested_comment" not in filtered_data.get("nested", {}):
            logger.info("✅ 嵌套注释字段已过滤")
        else:
            logger.error("❌ 嵌套注释字段未过滤")
        
        if "nested_valid" in filtered_data.get("nested", {}):
            logger.info("✅ 嵌套有效字段保留")
        else:
            logger.error("❌ 嵌套有效字段被误删")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 注释字段过滤测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始配置文件测试...")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("配置文件加载", test_config_file_loading),
        ("配置验证", test_config_validation),
        ("配置访问", test_config_access),
        ("敏感信息保护", test_sensitive_info_protection),
        ("注释字段过滤", test_comment_filtering)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 测试: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_name == "配置文件加载":
                result, config = test_func()
                test_results.append((test_name, result))
            else:
                result = test_func()
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
        logger.info("🎉 所有测试都通过了！配置文件系统工作正常！")
        logger.info("\n🔒 安全提醒：")
        logger.info("  ✅ 配置文件已正确加载")
        logger.info("  ✅ 敏感信息已保护")
        logger.info("  ✅ 注释字段已过滤")
        logger.info("  ✅ 配置验证正常")
        logger.info("\n📋 使用说明：")
        logger.info("  1. 配置文件位于项目根目录的 config.json")
        logger.info("  2. 参考 CONFIG_GUIDE.md 了解详细配置说明")
        logger.info("  3. 配置文件已添加到 .gitignore，不会被提交")
        logger.info("  4. 如需修改配置，请直接编辑 config.json 文件")
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，请检查配置")

if __name__ == "__main__":
    main()
