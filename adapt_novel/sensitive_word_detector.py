#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import random
from pypinyin import pinyin, Style

def detect_sensitive_words(novel_file_path, min_word_length=2):
    """
    检测小说文本中的敏感词并将敏感词中的一个随机汉字替换为拼音
    
    Args:
        novel_file_path (str): 小说文本文件的路径
        min_word_length (int): 敏感词的最小长度，默认为2，用于过滤单字敏感词
        
    Returns:
        str: 替换后的文件路径
    """
    # 读取小说文本
    try:
        with open(novel_file_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
    except Exception as e:
        print(f"读取小说文件出错: {e}")
        return None
    
    # 获取敏感词列表
    sensitive_words = []
    sensitive_words_dir = "/Users/heyi/adapt_novel_v2/sensitive_words"
    
    # 读取敏感词目录下的所有txt文件
    try:
        for sw_file in glob.glob(os.path.join(sensitive_words_dir, "*.txt")):
            with open(sw_file, 'r', encoding='utf-8') as f:
                words = f.read().splitlines()
                # 过滤空行
                words = [word.strip() for word in words if word.strip()]
                sensitive_words.extend(words)
    except Exception as e:
        print(f"读取敏感词文件出错: {e}")
        return None
    
    # 去重敏感词
    sensitive_words = list(set(sensitive_words))
    
    # 创建常用词白名单
    whitelist = ["人", "会", "小姐", "爱", "情", "性", "死", "好", "大", "小", "多", "少", "快", "慢"]
    
    # 过滤敏感词
    filtered_sensitive_words = []
    for word in sensitive_words:
        # 跳过空字符串
        if not word:  
            continue
        
        # 如果是汉字且长度小于最小长度，则跳过
        if len(word) < min_word_length and all('\u4e00' <= char <= '\u9fff' for char in word):
            continue
            
        # 如果在白名单中，则跳过
        if word in whitelist:
            continue
            
        filtered_sensitive_words.append(word)
    
    # 使用过滤后的敏感词列表
    sensitive_words = filtered_sensitive_words
    
    # 将敏感词中的随机一个字符替换为拼音
    replaced_text = novel_text
    for word in sensitive_words:
        if not word:  # 跳过空字符串
            continue
            
        # 逐字符匹配敏感词
        i = 0
        while i <= len(replaced_text) - len(word):
            # 检查是否匹配敏感词
            if replaced_text[i:i+len(word)] == word:
                # 随机选择敏感词中的一个汉字进行替换
                chinese_chars_indices = [j for j in range(len(word)) if '\u4e00' <= word[j] <= '\u9fff']
                
                if chinese_chars_indices:  # 确保有汉字可以替换
                    # 随机选择一个汉字的索引
                    random_index = random.choice(chinese_chars_indices)
                    char_to_replace = word[random_index]
                    
                    # 获取该汉字的拼音
                    char_pinyin = pinyin(char_to_replace, style=Style.NORMAL)[0][0]
                    
                    # 替换敏感词中的随机汉字为拼音
                    replaced_word = word[:random_index] + char_pinyin + word[random_index+1:]
                    replaced_text = replaced_text[:i] + replaced_word + replaced_text[i+len(word):]
                    
                    # 调整索引位置，跳过已替换的敏感词
                    i += len(replaced_word)
                else:
                    i += 1
            else:
                i += 1
    
    # 生成替换后的文件路径
    file_dir = os.path.dirname(novel_file_path)
    file_name = os.path.basename(novel_file_path)
    file_name_without_ext, file_ext = os.path.splitext(file_name)
    replaced_file_path = os.path.join(file_dir, f"{file_name_without_ext}_replaced{file_ext}")
    
    # 写入替换后的文本
    try:
        with open(replaced_file_path, 'w', encoding='utf-8') as f:
            f.write(replaced_text)
        print(f"敏感词替换完成，已保存到: {replaced_file_path}")
        return replaced_file_path
    except Exception as e:
        print(f"写入替换后的文件出错: {e}")
        return None

def main():
    """
    主函数，用于命令行调用
    """
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python sensitive_word_detector.py <小说文本路径>")
        return
    
    novel_file_path = sys.argv[1]
    detect_sensitive_words(novel_file_path)

if __name__ == "__main__":
    # 如果是直接运行这个脚本，则使用命令行参数
    main()