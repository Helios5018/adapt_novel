from openai import OpenAI

def get_response(model="qwen-max-latest", system_prompt=None, user_prompt=None, temperature=1, top_p=0.8):
    """
    model: 模型名称
    system_prompt: 系统提示词
    user_prompt: 用户提示词
    """
    client = OpenAI(
        api_key="sk-11b87320c63b4de183e5235355a30662",  # 如果您没有配置环境变量，请用百炼API Key将本行替换为：api_key="sk-xxx"
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
    )
    completion = client.chat.completions.create(
        model= model, 
        messages=[{'role': 'system', 'content': system_prompt},
                  {'role': 'user', 'content': user_prompt}],
        response_format = {"type": "json_object"},
        temperature= temperature,
        top_p= top_p
        )
    #print(completion.model_dump_json())
    return completion.model_dump_json()

if __name__ == '__main__':
    with open('/Users/heyi/adapt_novel_v2/prompt/降重改写v1.txt', 'r', encoding='utf-8') as file:
        system_prompt = str(file.read())
    with open('/Users/heyi/adapt_novel_v2/novel_result/云深不知情浅/intergrate_start_and_novel.txt', 'r', encoding='utf-8') as file:
        user_prompt = str(file.read())
    get_response(system_prompt=system_prompt, user_prompt=user_prompt)
