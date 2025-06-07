import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from call_any_llm import get_response, extract_response_result_message

def adapt_novel_by_segments(novel_file_path, target_length=1300, repeat_times=1):
    """    读取小说文本，按照指定长度分段，使用多线程方式调用大模型进行改写，然后合并结果并保存
    
    参数:
        novel_file_path (str): 小说文本文件路径
        target_length (int): 目标分隔长度，默认1300字
        repeat_times (int): 重复改写次数，默认为1次
        
    返回:
        list: 生成的所有新文件路径列表
    """
    # 读取小说文本
    try:
        with open(novel_file_path, 'r', encoding='utf-8') as file:
            novel_text = file.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []
    
    # 读取系统提示词
    system_prompt_path = '/Users/heyi/adapt_novel_v2/prompt/降重改写v1.txt'
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as file:
            system_prompt = file.read()
    except Exception as e:
        print(f"读取系统提示词失败: {e}")
        return []
    
    # 分段处理文本
    segments = split_novel_by_length(novel_text, target_length)
    print(f"小说已分为{len(segments)}段进行处理")
    
    # 使用多线程处理每个段落
    results = []
    all_segments_processed = True  # 标记是否所有段落都成功处理
    lock = threading.Lock()
    
    def process_segment(index, segment):
        nonlocal all_segments_processed
        try:
            print(f"正在处理第{index+1}段，长度: {len(segment)}字")
            response_json = get_response(system_prompt=system_prompt, user_prompt=segment, model="gemini-2.5-pro-preview-03-25") # 指定使用 gemini 模型
            # 首先检查响应是否表示错误
            try:
                response_data = json.loads(response_json)
                if isinstance(response_data, dict) and response_data.get("error"):
                    print(f"处理第{index+1}段时API返回错误: {response_data.get('error_detail', response_data.get('error_message'))}")
                    # 当API调用明确返回错误时，也应将all_segments_processed设为False
                    all_segments_processed = False # 标记处理失败
                    # 将原始段落存入结果，以便后续可能的调试或处理
                    with lock:
                        while len(results) <= index:
                            results.append(None)
                        results[index] = segment # 或者可以是None，取决于错误处理策略
                    return # 提前退出此段的处理
            except json.JSONDecodeError:
                # 如果响应不是有效的JSON（可能是网络问题或其他非标准错误响应），也标记失败
                print(f"处理第{index+1}段时响应非JSON格式，可能存在网络问题或API错误")
                all_segments_processed = False
                with lock:
                    while len(results) <= index:
                        results.append(None)
                    results[index] = segment
                return

            # 尝试提取大模型返回的内容
            content_text = extract_response_result_message(response_json)
            
            if content_text is None:
                print(f"处理第{index+1}段时无法从响应中提取有效内容，使用原文")
                adapted_text = segment
            else:
                # 尝试解析content_text（它本身可能是一个JSON字符串）
                try:
                    content_json = json.loads(content_text)
                    if isinstance(content_json, dict) and 'result' in content_json:
                        adapted_text = content_json['result']
                    else:
                        # 如果content_text是JSON但没有result字段，或者不是期望的格式，直接使用content_text
                        adapted_text = content_text
                except (json.JSONDecodeError, TypeError):
                    # 如果content_text不是JSON格式，直接使用它作为结果
                    adapted_text = content_text
            

            
            with lock:
                # 确保结果按原始顺序存储
                while len(results) <= index:
                    results.append(None)
                results[index] = adapted_text
                
            print(f"第{index+1}段处理完成")
        except Exception as e:
            print(f"处理第{index+1}段时出错: {e}")
            with lock:
                # 如果处理失败，标记处理状态为失败
                all_segments_processed = False
                print(f"处理第{index+1}段失败，整体处理将终止")
                # 仍然存储结果，以便于调试
                while len(results) <= index:
                    results.append(None)
                results[index] = segment
    
    # 创建线程池
    with ThreadPoolExecutor(max_workers=min(10, len(segments))) as executor:
        # 提交所有任务
        futures = [executor.submit(process_segment, i, segment) for i, segment in enumerate(segments)]
        
        # 等待所有任务完成
        for future in futures:
            future.result()
    
    # 检查是否所有段落都成功处理
    if not all_segments_processed:
        print("由于部分段落处理失败，不进行内容合成")
        return []
    
    # 检查是否有任何None值在结果中
    if None in results:
        print("结果中存在未处理的段落，不进行内容合成")
        return []
    
    # 初始化返回的文件路径列表
    generated_files = []
    
    # 循环执行指定次数的改写
    for iteration in range(1, repeat_times + 1):
        print(f"\n开始第 {iteration} 次改写...")
        
        # 每次都使用原始文本进行分段和处理
        if iteration > 1:
            # 重置处理状态和结果
            results = []
            all_segments_processed = True
            
            # 使用多线程处理每个段落
            with ThreadPoolExecutor(max_workers=min(10, len(segments))) as executor:
                # 提交所有任务
                futures = [executor.submit(process_segment, i, segment) for i, segment in enumerate(segments)]
                
                # 等待所有任务完成
                for future in futures:
                    future.result()
            
            # 检查是否所有段落都成功处理
            if not all_segments_processed:
                print(f"第 {iteration} 次改写中部分段落处理失败，不进行内容合成")
                break
            
            # 检查是否有任何None值在结果中
            if None in results:
                print(f"第 {iteration} 次改写中结果存在未处理的段落，不进行内容合成")
                break
        
        # 合并结果
        adapted_novel = ''.join(results)
        
        # 生成新文件名和路径
        file_dir = os.path.dirname(novel_file_path)
        file_name = os.path.basename(novel_file_path)
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        new_file_name = f"{file_name_without_ext}_adapted_{iteration}{file_ext}"
        new_file_path = os.path.join(file_dir, new_file_name)
        
        # 保存结果
        try:
            with open(new_file_path, 'w', encoding='utf-8') as file:
                file.write(adapted_novel)
            print(f"第 {iteration} 次改写完成，结果已保存至: {new_file_path}")
            generated_files.append(new_file_path)
        except Exception as e:
            print(f"保存第 {iteration} 次改写结果失败: {e}")
            break
    
    return generated_files

def split_novel_by_length(text, target_length=1000):
    """
    将小说文本按照指定长度进行分隔，在目标长度附近寻找句子结束符号（。！？）进行分隔
    
    参数:
        text (str): 需要分隔的小说文本
        target_length (int): 目标分隔长度，默认1000字
        
    返回:
        list: 分隔后的小说文本列表
    """
    result = []
    remaining_text = text
    
    while len(remaining_text) > target_length:
        # 从目标长度位置开始寻找句子结束符号
        cut_position = target_length
        found = False
        
        # 在目标长度后寻找最近的句子结束符号
        for i in range(cut_position, min(cut_position + 300, len(remaining_text))):
            if remaining_text[i] in ['。', '！', '？']:
                cut_position = i + 1  # 包含句子结束符号
                found = True
                break
        
        # 如果没找到结束符号，就在目标长度前寻找
        if not found:
            for i in range(cut_position - 1, max(0, cut_position - 300), -1):
                if remaining_text[i] in ['。', '！', '？']:
                    cut_position = i + 1  # 包含句子结束符号
                    found = True
                    break
        
        # 如果还是没找到，就直接在目标长度处截断
        if not found:
            cut_position = target_length
        
        # 添加分隔出的部分到结果列表
        result.append(remaining_text[:cut_position])
        # 更新剩余文本
        remaining_text = remaining_text[cut_position:]
    
    # 添加最后剩余的部分
    if remaining_text:
        result.append(remaining_text)
        
    return result

if __name__ == '__main__':
    # 测试示例
    novel_file_path = "/Users/heyi/Desktop/花溪小说/重生80.txt"
    adapt_novel_by_segments(novel_file_path, repeat_times=9)  # 测试重复改写3次

