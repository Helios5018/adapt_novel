from openai import OpenAI
from setup import *
import json

def get_response(user_prompt ,system_prompt=None, model="gemini-2.5-pro-preview-03-25", api_key = api_key_3, temperature=0.6, top_p=0.8, max_tokens=20000):
    """
    获取AI模型的响应，并提供详细的错误处理
    
    参数:
        model: 模型名称
        system_prompt: 系统提示词
        user_prompt: 用户提示词
    返回:
        成功时返回响应的JSON字符串，失败时返回包含错误信息的字典的JSON字符串
    """
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key = api_key, # TODO:设置为配置项
            base_url = default_base_url # TODO:设置为配置项
        )
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        if user_prompt:
            messages.append({'role': 'user', 'content': user_prompt})
        
        
        # 发送请求
        completion = client.chat.completions.create(
            model=model, 
            messages=messages,
            temperature= temperature,
            top_p= top_p,
            max_tokens= max_tokens,
            response_format = {"type": "json_object"}
        )
        
        response_json = completion.model_dump_json()
        return response_json
        
    except Exception as e:
        # 捕获所有可能的异常
        error_type = type(e).__name__
        error_msg = str(e)
        
        # 根据错误类型提供更详细的错误信息
        if "Connection" in error_type or "Timeout" in error_type:
            error_detail = "网络连接错误，请检查您的网络连接或API服务器是否可用"
        elif "Authentication" in error_type or "Unauthorized" in error_type or "api_key" in error_msg.lower():
            error_detail = "API密钥认证错误，请检查您的API密钥是否正确"
        elif "Rate" in error_type or "limit" in error_msg.lower():
            error_detail = "API请求频率超限，请稍后再试"
        elif "Invalid" in error_type or "parameter" in error_msg.lower() or "argument" in error_msg.lower():
            error_detail = "请求参数错误，请检查您的请求参数是否正确"
        elif "model" in error_msg.lower():
            error_detail = "模型错误，请检查模型名称是否正确或该模型是否可用"
        else:
            error_detail = "未知错误，请查看详细错误信息"
        
        # 构建错误信息
        error_info = {
            "error": True,
            "error_type": error_type,
            "error_message": error_msg,
            "error_detail": error_detail,
            "request_info": {
                "model": model,
                "system_prompt_length": len(system_prompt) if system_prompt else 0,
                "user_prompt_length": len(user_prompt) if user_prompt else 0
            }
        }
        
        # 打印详细错误信息
        print(f"\n请求失败! 错误类型: {error_type}")
        print(f"错误信息: {error_msg}")
        print(f"错误详情: {error_detail}")
        print(f"请求信息: 模型={model}, 系统提示词长度={len(system_prompt) if system_prompt else 0}, 用户提示词长度={len(user_prompt) if user_prompt else 0}\n")
        
        return json.dumps(error_info, ensure_ascii=False)

def extract_response_result_message(response_result):
    try:
        # 检查输入是否为None
        if response_result is None:
            print("输入为None，无法解析JSON")
            return None
            
        # 解析API返回的JSON字符串
        parsed_data = json.loads(response_result)
        
        # 检查是否有choices字段
        if "choices" in parsed_data and len(parsed_data["choices"]) > 0:
            # 获取第一个choice
            choice = parsed_data["choices"][0]
            
            # 检查是否有message字段
            if "message" in choice and "content" in choice["message"]:
                # 获取content内容
                content = choice["message"]["content"]
                # 返回content内容
                return content
            else:
                print("未找到message.content字段")
                return None
        else:
            # 检查是否直接包含result字段（兼容旧格式）
            if "result" in parsed_data:
                return parsed_data["result"]
            else:
                print("未找到choices字段或result字段")
                return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return None

if __name__ == '__main__':
    s_p = "你是一个智能助手"
    u_p = "3.11和3.9，哪个大"
    response = get_response(model="qwen3-235b-a22b", api_key=api_key_1, system_prompt=s_p, user_prompt=u_p)
    print(response)
    print(extract_response_result_message(response))
