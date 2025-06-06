"""
数据处理器模块

这个模块提供了文本数据处理的核心功能，主要用于：
1. 文本验证：检查输入文本的有效性
2. 标记添加：为文本添加处理标识和时间戳
3. 格式化处理：统一文本格式和结构

技术特点：
- 支持自定义处理标记
- 可选的时间戳功能
- 完整的输入验证
- 详细的日志记录
- 简洁的API设计

使用场景：
- AI处理结果标记
- 文本预处理
- 数据格式化
- 处理状态跟踪

作者：MCP图像识别系统
版本：1.0.0
"""

import logging                    # 日志记录
from datetime import datetime     # 时间戳生成
from typing import Optional       # 类型注解

# ==================== 日志配置 ====================
# 使用现有的日志配置，确保与整个系统的日志策略一致
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    数据处理器

    这个类提供了文本数据处理的核心功能，包括文本验证、
    标记添加和格式化处理。设计简洁易用，支持扩展。

    主要功能：
    - 文本有效性验证
    - 添加处理标识和时间戳
    - 支持自定义标记格式
    - 提供详细的处理日志
    """

    def __init__(self):
        """
        初始化数据处理器

        创建处理器实例，设置默认配置。
        当前版本不需要特殊配置，但为未来扩展预留接口。
        """
        logger.info("🔧 数据处理器初始化完成")
    
    def add_processed_marker(self, original_text: str, add_timestamp: bool = True) -> str:
        """
        为原始文本添加处理标识

        这个方法为输入的文本添加处理标记，用于标识文本已经被系统处理过。
        支持可选的时间戳功能，便于跟踪处理时间。

        处理逻辑：
        1. 验证输入文本是否为空
        2. 根据参数决定是否添加时间戳
        3. 构造带标识的文本
        4. 记录处理日志

        Args:
            original_text: 需要添加标识的原始文本
            add_timestamp: 是否在标识中包含时间戳，默认为True

        Returns:
            str: 添加了处理标识的文本

        Examples:
            >>> processor = DataProcessor()
            >>> processor.add_processed_marker("测试文本", True)
            "[已处理-2025-01-15 10:30:45] 测试文本"
            >>> processor.add_processed_marker("测试文本", False)
            "[已处理] 测试文本"
        """
        # ==================== 输入验证 ====================
        if not original_text:
            logger.warning("⚠️ 输入文本为空，返回默认标识")
            return "[已处理] (空内容)"

        logger.info(f"🔄 开始为文本添加处理标识")
        logger.info(f"📝 原始文本: {original_text[:100]}...")  # 只显示前100字符

        # ==================== 构造处理标识 ====================
        if add_timestamp:
            # 生成当前时间戳，格式：YYYY-MM-DD HH:MM:SS
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            processed_text = f"[已处理-{timestamp}] {original_text}"
            logger.info(f"⏰ 添加时间戳: {timestamp}")
        else:
            # 不添加时间戳，使用简单标识
            processed_text = f"[已处理] {original_text}"
            logger.info("🏷️ 使用简单标识")

        logger.info(f"✅ 处理完成，结果长度: {len(processed_text)} 字符")
        logger.info(f"📄 处理结果预览: {processed_text[:100]}...")

        return processed_text
    
    def validate_text(self, text: str) -> bool:
        """
        验证文本是否有效

        这个方法检查输入文本的有效性，确保文本不为空且包含有意义的内容。
        用于在处理前验证输入，避免处理无效数据。

        验证规则：
        1. 文本不能为None
        2. 文本不能为空字符串
        3. 文本去除空白字符后不能为空

        Args:
            text: 需要验证的文本字符串

        Returns:
            bool: 如果文本有效返回True，否则返回False

        Examples:
            >>> processor = DataProcessor()
            >>> processor.validate_text("有效文本")
            True
            >>> processor.validate_text("")
            False
            >>> processor.validate_text("   ")
            False
            >>> processor.validate_text(None)
            False
        """
        logger.info(f"🔍 开始验证文本有效性")

        # ==================== 文本有效性检查 ====================
        if not text or not text.strip():
            # 文本为空、None或只包含空白字符
            logger.warning("❌ 文本验证失败: 文本为空或只包含空白字符")
            logger.warning(f"📝 输入内容: '{text}'")
            return False

        # 文本验证通过
        logger.info("✅ 文本验证通过")
        logger.info(f"📝 文本长度: {len(text)} 字符")
        logger.info(f"📄 文本预览: {text[:50]}...")  # 显示前50字符

        return True
