from call_any_llm import get_response, extract_response_result_message
import os
import ast

class AdaptNovel():
    def __init__(self, novel_name, original_novel = None, original_novel_txt = None):
        # 初始化小说名称和原始小说
        self.novel_name = novel_name
        if original_novel_txt:
            with open(original_novel_txt, 'r', encoding='utf-8') as file:
                self.original_novel = file.read()
        else:
            if original_novel:
                self.original_novel = original_novel
            else:
                print("请输入原始小说或提供原始小说txt文件")
                return
        # 创建文件夹
        path = os.path.join('novel_result', str(self.novel_name))
        if not os.path.exists(path):
            os.makedirs(path)
            
        # 判断小说长度是否大于2000字
        if len(self.original_novel) > 2000:
            # 分隔小说文本
            novel_parts = self.split_novel_by_length(self.original_novel, 2000)
            # 保存分隔后的小说文本
            for i, part in enumerate(novel_parts, 1):
                with open(os.path.join(path, f'original_novel_{i}.txt'), 'w', encoding='utf-8') as file:
                    file.write(part)
            # 同时保存完整的原始小说
            with open(os.path.join(path, 'original_novel.txt'), 'w', encoding='utf-8') as file:
                file.write(str(self.original_novel))
        else:
            # 如果小于2000字，直接保存原始小说
            with open(os.path.join(path, 'original_novel_1.txt'), 'w', encoding='utf-8') as file:
                file.write(str(self.original_novel))
            # 创建原始小说文本txt文件
            with open(os.path.join(path, 'original_novel.txt'), 'w', encoding='utf-8') as file:
                file.write(str(self.original_novel))
        print("小说初始化完成")
        
    def split_novel_by_length(self, text, target_length=2000):
        """
        将小说文本按照指定长度进行分隔，在目标长度附近寻找句子结束符号（。！？）进行分隔
        
        参数:
            text (str): 需要分隔的小说文本
            target_length (int): 目标分隔长度，默认2000字
            
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

    def get_brilliant_start(self):
        # 构建系统提示词
        # 打开文件并读取内容
        with open('prompt/写精彩开头v1.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        # 构建用户提示
        if self.original_novel:
            user_prompt = self.original_novel
        else:
            try:
                with open(os.path.join('novel_result', str(self.novel_name), 'original_novel_1.txt'), 'r', encoding='utf-8') as file:
                    user_prompt = file.read()
            except:
                print("请输入原始小说或提供原始小说txt文件")
                return
        # 调用LLM获取结果
        response = get_response(user_prompt= user_prompt,system_prompt=system_prompt)
        result = extract_response_result_message(response)
        # 将结果保存到txt文件
        with open(os.path.join('novel_result', str(self.novel_name), 'brilliant_start.txt'), 'w', encoding='utf-8') as file:
            file.write(str(result))
        print("精彩开头生成完成")
        return result

    @staticmethod
    def process_file(novel_name, file_index, system_prompt):
        """
        处理单个文件的函数，用于多进程调用
        
        参数:
            novel_name (str): 小说名称
            file_index (int): 文件索引
            system_prompt (str): 系统提示词
            
        返回:
            str: 处理后的小说文本，如果处理失败则返回None
        """
        # 构建文件路径
        file_path = os.path.join('novel_result', str(novel_name), f'original_novel_{file_index}.txt')
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                user_prompt = file.read()
        except:
            print(f"无法读取文件: {file_path}")
            return None
        
        # 调用LLM获取结果
        response = get_response(user_prompt=user_prompt, system_prompt=system_prompt)
        extracted_message = extract_response_result_message(response)
        if extracted_message is None:
            print(f"从LLM获取内容失败，文件索引: {file_index}")
            return None
        try:
            result = ast.literal_eval(extracted_message)['first_perspective_novel']
        except (ValueError, SyntaxError) as e:
            print(f"解析LLM响应时出错 (文件索引: {file_index}): {e}")
            print(f"原始响应内容: {extracted_message}")
            return None
        
        # 将结果保存到对应的txt文件
        output_path = os.path.join('novel_result', str(novel_name), f'first_perspective_novel_{file_index}.txt')
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(str(result))
        
        print(f"第一人称小说生成完成: {file_index}")
        return result
        
    def get_first_perspective_novel(self):
        # 导入多进程模块
        import multiprocessing
        from multiprocessing import Pool
        import glob
        
        # 构建系统提示词
        # 打开文件并读取内容
        with open('prompt/人称改写v1.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        
        # 获取所有需要处理的文件索引
        path = os.path.join('novel_result', str(self.novel_name))
        file_pattern = os.path.join(path, 'original_novel_*.txt')
        files = glob.glob(file_pattern)
        # 提取文件索引
        indices = [int(f.split('_')[-1].split('.')[0]) for f in files if '_' in f and not f.endswith('original_novel.txt')]
        
        if not indices:
            print("未找到分段小说文件")
            return None
        
        # 使用多进程处理所有文件
        results = []
        # 获取CPU核心数，设置进程池大小
        num_processes = min(multiprocessing.cpu_count(), len(indices))
        
        # 创建进程池并执行任务
        with Pool(processes=num_processes) as pool:
            # 为每个文件索引创建参数元组 (novel_name, file_index, system_prompt)
            args = [(self.novel_name, idx, system_prompt) for idx in indices]
            results = pool.starmap(AdaptNovel.process_file, args)
        
        # 合并所有结果并保存到完整的文件中
        combined_result = '\n'.join([r for r in results if r is not None])
        with open(os.path.join('novel_result', str(self.novel_name), 'first_perspective_novel.txt'), 'w', encoding='utf-8') as file:
            file.write(str(combined_result))
        
        print("所有第一人称小说生成完成并合并")
        return combined_result

    def intergrate_start_and_novel(self, use_original_novel = False, use_first_perspective_novel = False, start_id = 0):
        # 构建系统提示词
        # 打开文件并读取内容
        with open('prompt/开头与正文融合v1.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        # 构建用户提示
        try:
            with open(os.path.join('novel_result', str(self.novel_name), 'brilliant_start.txt'), 'r', encoding='utf-8') as file:
                brilliant_start_content = file.read()
                if not brilliant_start_content:
                    print("brilliant_start.txt 文件为空")
                    return None
                try:
                    all_start = ast.literal_eval(brilliant_start_content)
                except (ValueError, SyntaxError) as e:
                    print(f"解析 brilliant_start.txt 时出错: {e}")
                    print(f"文件内容: {brilliant_start_content}")
                    return None
                key = f'brilliant_start_{start_id}'
                start = all_start[key]
            # 选择使用原始小说还是第一人称小说
            if use_original_novel:
                with open(os.path.join('novel_result', str(self.novel_name), 'original_novel_1.txt'), 'r', encoding='utf-8') as file:
                    novel = file.read()
            elif use_first_perspective_novel:
                with open(os.path.join('novel_result', str(self.novel_name), 'first_perspective_novel_1.txt'), 'r', encoding='utf-8') as file:
                    novel = file.read()
            else:
                print("请选择使用原始小说还是第一人称小说")
                return
            # 拼装用户提示
            user_prompt = f"精彩开头：{start}\n小说正文：{novel}"
        except FileNotFoundError as e:
            print(f"文件未找到错误: {e}。请确保 brilliant_start.txt, original_novel_1.txt 或 first_perspective_novel_1.txt 文件存在。")
            return
        except KeyError as e:
            print(f"字典键错误: {e}。请检查 brilliant_start.txt 中的 'brilliant_start_{start_id}' 是否存在。")
            return
        except Exception as e:
            print(f"在准备用户提示词时发生未知错误: {e}")
            return
        # 调用LLM获取结果
        response = get_response(user_prompt= user_prompt ,system_prompt=system_prompt)
        extracted_message_part1 = extract_response_result_message(response)
        if extracted_message_part1 is None:
            print("从LLM获取开头融合内容失败")
            return None # 或者根据需要处理错误
        try:
            result_part1 = ast.literal_eval(extracted_message_part1)['intergrate_start_and_novel']
        except (ValueError, SyntaxError) as e:
            print(f"解析LLM响应时出错 (开头融合): {e}")
            print(f"原始响应内容: {extracted_message_part1}")
            return None # 或者根据需要处理错误
        # 将第一部分结果保存到txt文件
        intergrate_part1_path = os.path.join('novel_result', str(self.novel_name), 'intergrate_start_and_novel_1.txt')
        with open(intergrate_part1_path, 'w', encoding='utf-8') as file:
            file.write(str(result_part1))
        print("开头与正文第一部分融合生成完成")

        # 合并剩余部分
        full_integrated_novel = result_part1
        novel_dir = os.path.join('novel_result', str(self.novel_name))
        
        # 获取所有分段文件的数量
        original_files_pattern = os.path.join(novel_dir, 'original_novel_*.txt')
        import glob
        original_files = [f for f in glob.glob(original_files_pattern) if not f.endswith('original_novel.txt')]
        num_parts = len(original_files)

        if num_parts > 1:
            for i in range(2, num_parts + 1):
                part_content = ""
                if use_original_novel:
                    part_file_path = os.path.join(novel_dir, f'original_novel_{i}.txt')
                    try:
                        with open(part_file_path, 'r', encoding='utf-8') as file:
                            part_content = file.read()
                    except FileNotFoundError:
                        print(f"未找到文件: {part_file_path}")
                        continue
                elif use_first_perspective_novel:
                    part_file_path = os.path.join(novel_dir, f'first_perspective_novel_{i}.txt')
                    try:
                        with open(part_file_path, 'r', encoding='utf-8') as file:
                            part_content = file.read()
                    except FileNotFoundError:
                        print(f"未找到文件: {part_file_path}")
                        continue
                full_integrated_novel += "\n" + part_content

        # 将完整融合后的小说保存到txt文件
        with open(os.path.join(novel_dir, 'intergrate_start_and_novel.txt'), 'w', encoding='utf-8') as file:
            file.write(full_integrated_novel)
        print("开头与正文完整融合生成完成")
        return full_integrated_novel

if __name__ == "__main__":
    run_novel_ = AdaptNovel(novel_name= "血玫瑰", original_novel_txt= "/Users/heyi/adapt_novel_v2/小说list/血玫瑰.txt")
    #run_novel_.get_brilliant_start()
    run_novel_.intergrate_start_and_novel(use_original_novel= True,start_id=4)
