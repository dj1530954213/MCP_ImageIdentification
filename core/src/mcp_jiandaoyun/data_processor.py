"""
数据处理器

提供简单的数据处理功能，主要是添加处理标识。
"""

import logging
from datetime import datetime
from typing import Optional

# 配置日志
logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        logger.info("数据处理器初始化完成")
    
    def add_processed_marker(self, original_text: str, add_timestamp: bool = True) -> str:
        """
        为原始文本添加处理标识
        
        Args:
            original_text: 原始文本
            add_timestamp: 是否添加时间戳
            
        Returns:
            添加标识后的文本
        """
        if not original_text:
            logger.warning("输入文本为空")
            return "[已处理] (空内容)"
        
        logger.info(f"开始处理文本: {original_text}")
        
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            processed_text = f"[已处理-{timestamp}] {original_text}"
        else:
            processed_text = f"[已处理] {original_text}"
        
        logger.info(f"处理完成: {processed_text}")
        return processed_text
    
    def validate_text(self, text: str) -> bool:
        """
        验证文本是否有效
        
        Args:
            text: 要验证的文本
            
        Returns:
            是否有效
        """
        if not text or not text.strip():
            logger.warning("文本验证失败: 文本为空或只包含空白字符")
            return False
        
        logger.info("文本验证通过")
        return True
