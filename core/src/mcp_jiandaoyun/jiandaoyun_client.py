"""
简道云 API 客户端

提供简道云数据查询和创建功能。
"""

import logging
from typing import List, Dict, Any, Optional
import httpx

# 配置日志 - 使用现有的日志配置
logger = logging.getLogger(__name__)

class JianDaoYunClient:
    """简道云 API 客户端"""
    
    def __init__(self):
        # 硬编码配置 - 使用您提供的测试过的配置
        self.api_key = "WuVMLm7r6s1zzFTkGyEYXQGxEZ9mLj3h"
        self.app_id = "67d13e0bb840cdf11eccad1e"
        self.entry_id = "683ff705c700b55c74bb24ab"
        self.source_field = "_widget_1749016991917"  # 数据源字段
        self.result_field = "_widget_1749016991918"  # 接收结果字段
        
        # API 端点
        self.query_url = "https://api.jiandaoyun.com/api/v5/app/entry/data/list"
        self.create_url = "https://api.jiandaoyun.com/api/v5/app/entry/data/create"
        
        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info("简道云客户端初始化完成")
        logger.info(f"应用ID: {self.app_id}")
        logger.info(f"表单ID: {self.entry_id}")
    
    async def query_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询简道云数据
        
        Args:
            limit: 查询数据条数限制
            
        Returns:
            查询到的数据列表
        """
        logger.info(f"开始查询简道云数据，限制条数: {limit}")
        
        request_body = {
            "app_id": self.app_id,
            "entry_id": self.entry_id,
            "data_id": "",
            "fields": [self.source_field, self.result_field],
            "filter": {
                "rel": "and",
                "cond": []
            },
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"发送请求到: {self.query_url}")
                logger.debug(f"请求体: {request_body}")
                
                response = await client.post(
                    self.query_url,
                    json=request_body,
                    headers=self.headers,
                    timeout=30.0
                )
                
                logger.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"查询成功，返回 {len(data.get('data', []))} 条数据")
                    return data.get('data', [])
                else:
                    logger.error(f"查询失败，状态码: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    raise Exception(f"查询数据失败: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"查询数据时发生错误: {str(e)}")
            raise
    
    async def create_data(self, source_text: str, result_text: str) -> Dict[str, Any]:
        """
        创建新的简道云数据
        
        Args:
            source_text: 数据源内容
            result_text: 处理结果内容
            
        Returns:
            创建结果
        """
        logger.info(f"开始创建简道云数据")
        logger.info(f"数据源内容: {source_text}")
        logger.info(f"处理结果内容: {result_text}")
        
        request_body = {
            "app_id": self.app_id,
            "entry_id": self.entry_id,
            "data": {
                self.source_field: {
                    "value": source_text
                },
                self.result_field: {
                    "value": result_text
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"发送请求到: {self.create_url}")
                logger.debug(f"请求体: {request_body}")
                
                response = await client.post(
                    self.create_url,
                    json=request_body,
                    headers=self.headers,
                    timeout=30.0
                )
                
                logger.info(f"API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("数据创建成功")
                    logger.debug(f"响应数据: {data}")
                    return data
                else:
                    logger.error(f"创建失败，状态码: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    raise Exception(f"创建数据失败: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"创建数据时发生错误: {str(e)}")
            raise
