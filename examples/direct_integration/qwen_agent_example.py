from typing import Any
import httpx
import asyncio
# from mcp.server.fastmcp import FastMCP # 不再需要 FastMCP 服务器

# Qwen-Agent 相关导入
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print
import json5 # 用于解析LLM生成的参数

# Initialize FastMCP server # 不再需要
# mcp = FastMCP("weather")

# API Key 和常量保持不变
OPENWEATHER_API_KEY = "552a88ef3f12c77dae8ffa0903080456" # 将你的Key硬编码在这里或从配置读取
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
USER_AGENT = "weather-app/1.0"

# 异步请求函数 (基本保持不变, 确保API Key正确传入)
async def make_weather_request(endpoint: str, params: dict[str, str]) -> dict[str, Any] | None:
    """向OpenWeather API发送请求
    Args:
        endpoint (str): API端点，如 "weather" 或 "forecast"
        params (dict[str, str]): 请求参数，如城市名、语言等

    Returns:
        dict[str, Any] | None: 返回的 JSON 数据，如果请求失败则返回 None
    """
    # 确保添加API密钥，如果它没有在params中
    if "appid" not in params:
        params["appid"] = OPENWEATHER_API_KEY

    url = f"{OPENWEATHER_API_BASE}/{endpoint}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            print(f"请求超时 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                print("已达到最大重试次数，放弃请求")
                return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e}")
            return None
        except Exception as e:
            print(f"请求失败: {e}") # 更通用的错误捕获
            return None
    return None # 确保函数总有返回值

# 天气数据格式化函数 (基本保持不变)
def format_weather(data: dict) -> str:
    """将OpenWeather API返回的天气数据格式化为可读字符串

    Args:
        data (dict): OpenWeather API返回的JSON格式天气数据

    Returns:
        str: 格式化后的天气信息文本
    """
    if not data:
        return "无法获取天气信息"

    try:
        city_name = data.get("name", "未知城市")
        country = data.get("sys", {}).get("country", "未知国家")
        
        # API默认返回开尔文，如果请求时指定了 units="metric"，则已经是摄氏度
        # get_weather_logic 中我们指定了 units="metric"
        temp_celsius = data.get("main", {}).get("temp", 0) 

        weather_desc = data.get("weather", [{}])[0].get("description", "未知天气状况")
        humidity = data.get("main", {}).get("humidity", 0)
        wind_speed = data.get("wind", {}).get("speed", 0)

        return f"""
城市: {city_name}, {country}
天气: {weather_desc}
温度: {temp_celsius:.1f}°C
湿度: {humidity}%
风速: {wind_speed} m/s
"""
    except Exception as e:
        return f"格式化天气数据时出错: {e}"

# 原 get_weather 函数的核心逻辑，不再是 MCP tool
async def get_weather_logic(city: str) -> str:
    """获取指定城市的天气信息 (核心逻辑)

    Args:
        city: 城市名称(例如：Beijing，Shanghai)
    Returns:
        str: 天气信息文本
    """
    if not city or len(city.strip()) == 0:
        return "请提供有效的城市名称"

    original_city = city # 保留原始城市名
    city_for_api = city
    # 临时处理中文"北京"到英文"Beijing"
    if city == "北京":
        print(f"检测到城市为 '{original_city}'，将使用 'Beijing' 进行API查询。")
        city_for_api = "Beijing"
    elif city.lower() == "beijing": # 也标准化一下可能的英文输入
        city_for_api = "Beijing" 

    params = {
        "q": city_for_api, # 使用处理后的 city_for_api
        "lang": "zh_cn",
        "units": "metric" # 确保获取摄氏度
    }
    # API Key 会在 make_weather_request 中自动添加

    try:
        data = await make_weather_request("weather", params)
        if not data:
            return f"无法获取{city}的天气信息，请检查城市名称是否正确或稍后再试。"
        return format_weather(data)
    except Exception as e:
        return f"获取天气信息时发生错误: {str(e)}"

# Qwen-Agent 自定义工具
@register_tool('mcp_weather_tool')
class MCPWeatherTool(BaseTool):
    description = '获取指定城市的天气信息。当你需要查询某个城市的天气时使用这个工具。'
    parameters = [{
        'name': 'city',
        'type': 'string',
        'description': '需要查询天气的城市名称，例如：北京、伦敦、东京。',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        print(f"\n[MCPWeatherTool LOG] 收到调用请求，参数: {params}") # 新增日志
        # params 是 LLM 生成的参数字符串，格式为 JSON
        try:
            param_dict = json5.loads(params)
            city = param_dict.get('city')
            if not city:
                error_msg = '调用天气工具失败：缺少城市名称参数 (city)'
                print(f"[MCPWeatherTool LOG] {error_msg}") # 新增日志
                return json5.dumps({'error': error_msg}, ensure_ascii=False)

            print(f"[MCPWeatherTool LOG] 正在为城市 '{city}' 查询天气...") # 新增日志

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:  # No running event loop
                loop = None

            if loop and loop.is_running():
                result = asyncio.run(get_weather_logic(city))
            else: 
                result = asyncio.run(get_weather_logic(city))
            
            print(f"[MCPWeatherTool LOG] 成功获取并处理了 '{city}' 的天气数据。") # 新增日志
            # print(f"[MCPWeatherTool LOG] 返回给LLM的数据: {result}") # 可选：打印返回给LLM的数据，可能会很长
            return result

        except json5.JSONDecodeError as e:
            error_msg = f'调用天气工具失败：参数格式错误，期望JSON格式。错误: {e}'
            print(f"[MCPWeatherTool LOG] {error_msg}") # 新增日志
            return json5.dumps({'error': error_msg}, ensure_ascii=False)
        except Exception as e:
            error_msg = f'调用天气工具时发生未知内部错误: {str(e)}'
            print(f"[MCPWeatherTool LOG] {error_msg}") # 新增日志
            return json5.dumps({'error': error_msg}, ensure_ascii=False)


# Agent 配置和运行的主函数
def run_qwen_agent_with_weather_tool():
    # 1. 配置 LLM
    # !!! 请务必将下面的 'model', 'model_server', 'api_key', 和 'model_type' 修改为你的实际配置 !!!
    llm_cfg = {
        'model': 'qwen3:8b',  # 示例: 'Qwen2.5-7B-Instruct', 'qwen1.5-7b-chat' 等
        'model_server': 'http://127.0.0.1:11434/v1', # 修改：添加 /v1 以正确指向Ollama的OpenAI兼容API端点
        'api_key': 'EMPTY', # 对于大多数本地服务，此项为 'EMPTY' 或不需要
        
        # 如果你的本地服务是 OpenAI API 兼容的，通常需要指定 model_type
        # 查阅 Qwen-Agent 文档获取支持的 model_type，常见的有 'openai', 'qianwen' (用于通义官方API)
        # 对于本地 OpenAI 兼容服务（如 vLLM, Ollama），'openai' 通常是正确的
        'model_type': 'oai', # 修改：根据错误提示，将 'openai' 修改为 'oai' 以适配Ollama

        'generate_cfg': { # 可选的生成参数
            'top_p': 0.8,
            # 'temperature': 0.7, # 如果需要可以添加
        }
    }
    print("--- LLM 配置 ---")
    print(f"模型: {llm_cfg.get('model')}")
    print(f"模型服务地址: {llm_cfg.get('model_server')}")
    print(f"模型类型: {llm_cfg.get('model_type')}")
    print("--------------------")


    # 2. 创建 Agent
    system_instruction = (
        "你是一个AI助手。你可以调用工具来帮助用户。"
        "当你需要获取实时天气信息时，请使用 'mcp_weather_tool' 工具。"
        "请直接使用工具返回的信息作为答案，不要添加额外的解释，除非信息不完整或有错误。"
        "如果工具调用失败或返回错误信息，请如实告知用户。"
    )
    
    # function_list 需要传入注册的工具名称列表
    available_tools = ['mcp_weather_tool']

    try:
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction,
            function_list=available_tools
        )
    except Exception as e:
        print(f"创建Agent失败: {e}")
        print("请检查LLM配置（model, model_server, api_key, model_type）是否正确，以及Qwen-Agent是否正确安装。")
        return

    # 3. 运行 Agent 聊天机器人
    messages = []
    print("\n你好！我是你的天气助手。你可以问我任何城市的天气，例如：'北京今天天气怎么样？'。输入 '退出' 来结束程序。")
    
    while True:
        try:
            query = input('\n用户: ')
            if query.strip().lower() == '退出':
                print("再见！")
                break
            if not query.strip():
                continue

            messages.append({'role': 'user', 'content': query})
            
            print('助手: ', end='', flush=True)
            
            response_stream = bot.run(messages=messages)
            
            # 根据官方示例，用于 typewriter_print 的累积纯文本
            cumulative_printed_text_for_typewriter = ""
            # 用于存储从流中获取的最后一个非空响应块，通常包含完整的结构化消息
            last_response_chunk_for_history = None

            for chunk_list in response_stream:
                # 直接将原始 chunk_list 和累积文本传递给 typewriter_print
                # 期望它内部处理增量打印和累积
                try:
                    cumulative_printed_text_for_typewriter = typewriter_print(
                        chunk_list,  # 原始响应块
                        cumulative_printed_text_for_typewriter # 上一次累积的纯文本
                    )
                    # 记录最后一次非空的 chunk_list，因为它可能包含完整的消息结构
                    if chunk_list: # 确保 chunk_list 不是 None 或空的
                        last_response_chunk_for_history = chunk_list
                except Exception as e_tp_inner:
                    # 如果 typewriter_print 失败，尝试打印原始 content (如果可提取)
                    raw_content_fallback = ""
                    if isinstance(chunk_list, list):
                        for item in chunk_list:
                            if isinstance(item, dict) and item.get('role') == 'assistant':
                                raw_content_fallback += str(item.get('content', ''))
                    elif isinstance(chunk_list, dict):
                        if chunk_list.get('role') == 'assistant':
                            raw_content_fallback += str(chunk_list.get('content', ''))

                    print(f"\n调用 typewriter_print 失败: {e_tp_inner}. Fallback 输出: {raw_content_fallback}", end='', flush=True)
                    # 在fallback时，我们也需要累积，尽管效果可能不佳
                    cumulative_printed_text_for_typewriter += raw_content_fallback
                    if chunk_list:
                        last_response_chunk_for_history = chunk_list
            
            print() # 确保在助手所有回复片段结束后换行

            # 更新对话历史
            # 根据Qwen-Agent示例，messages.extend(response) 中的 response 是最后一块。
            # last_response_chunk_for_history 应该是流的最后一块，它可能是一个包含消息字典的列表
            if last_response_chunk_for_history:
                if isinstance(last_response_chunk_for_history, list): # 如官方示例 response = [] ... messages.extend(response)
                    # 假设列表中的每个元素都是一个消息字典
                    # 我们只添加 role 为 assistant 的部分，并且确保 content 存在
                    added_to_history = False
                    for msg_item in last_response_chunk_for_history:
                        if isinstance(msg_item, dict) and msg_item.get('role') == 'assistant' and msg_item.get('content') is not None:
                            messages.append(msg_item)
                            added_to_history = True
                    if not added_to_history and cumulative_printed_text_for_typewriter.strip():
                        # 如果最后一块没有直接可用的 assistant 消息，但有打印过文本，
                        # 使用累积的纯文本作为历史记录 (这可能不如结构化消息好，但聊胜于无)
                        messages.append({'role': 'assistant', 'content': cumulative_printed_text_for_typewriter.strip()})
                elif isinstance(last_response_chunk_for_history, dict) and \
                     last_response_chunk_for_history.get('role') == 'assistant' and \
                     last_response_chunk_for_history.get('content') is not None: # 如果最后一块本身就是一个消息字典
                    messages.append(last_response_chunk_for_history)
                elif cumulative_printed_text_for_typewriter.strip():
                    # 如果流中没有任何 chunk 被记录为 last_response_chunk_for_history (例如流为空或者所有 chunk 都是 None)
                    # 但 typewriter_print 确实输出了内容 (例如，通过 fallback 逻辑)
                    messages.append({'role': 'assistant', 'content': cumulative_printed_text_for_typewriter.strip()})

        except KeyboardInterrupt:
            print("\n再见！程序已由用户中断。")
            break
        except Exception as e: # 确保 try 有对应的 except
            print(f"\n发生未预料的错误: {e}")
            import traceback
            traceback.print_exc()
            # 可选：messages = [] # 清空历史以避免错误状态传递


# @mcp.tool() # 不再是MCP tool
# async def get_weather(city: str) -> str:
# ... (这部分逻辑已经移到 get_weather_logic)


if __name__ == "__main__":
    # 使用 SSE 传输方式启动服务器，以便与测试界面兼容 # 不再需要 FastMCP 服务器
    # mcp.run(transport="stdio")
    
    # 运行新的 Qwen-Agent 主函数
    run_qwen_agent_with_weather_tool()
