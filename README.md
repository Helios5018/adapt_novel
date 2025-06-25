# Adapt Novel 项目

## 项目简介

`Adapt Novel` 是一个使用大型语言模型（LLM）对小说文本进行自动化改写和处理的 Python 项目。它可以实现以下主要功能：

*   **小说初始化与分段**：根据设定长度（默认为2000字）对原始小说进行分段，便于后续处理。
*   **生成精彩开头**：调用 LLM 为小说生成一个引人入胜的开头。
*   **第一人称改写**：将小说从第三人称（或其他）改写为第一人称视角。
*   **小说内容降重与改写**：对小说文本进行分段，并调用 LLM 进行降重和风格改写。
*   **敏感词检测**：检测文本中的敏感词。
*   **开头与正文融合**：将生成的精彩开头与改写后的正文进行融合。
*   **自动精简**：对文本进行精简，去除冗余内容。

项目通过读取 `prompt` 文件夹下的不同提示词文件来指导 LLM 完成特定任务，并将处理结果保存在 `novel_result` 文件夹下，按小说名称分子文件夹进行管理。

## 项目结构

```
adapt_novel/
├── .gitignore          # Git忽略文件配置
├── .venv/              # Python虚拟环境 (可选)
├── adapt_novel/        # 项目核心代码目录
│   ├── __init__.py
│   ├── adapt_novel_main.py  # 主要逻辑实现，包括小说初始化、生成开头、第一人称改写等
│   ├── call_any_llm.py      # 调用通用LLM接口的封装
│   ├── call_qwen_llm.py     # 调用特定Qwen LLM接口的封装 (可能已整合或废弃)
│   ├── novel_adapter.py     # 小说改写核心逻辑，包括分段、多线程/多进程调用LLM进行改写
│   ├── novel_result/        # 存放处理后的小说结果
│   │   ├── [小说名称1]/     # 例如：云深不知情浅
│   │   │   ├── brilliant_start.txt            # 生成的精彩开头
│   │   │   ├── intergrate_start_and_novel.txt # 开头与正文融合结果
│   │   │   ├── original_novel.txt             # 原始小说完整版
│   │   │   ├── original_novel_1.txt           # 原始小说分段1
│   │   │   └── ...
│   │   └── [小说名称2]/     # 其他小说结果
│   ├── sensitive_word_detector.py # 敏感词检测功能
│   └── setup.py             # 项目打包配置文件 (可能未使用或不完整)
├── novel_result/         # (与 adapt_novel/novel_result/ 结构类似，可能是冗余或不同阶段的输出)
├── prompt/               # 存放LLM的提示词文件
│   ├── 人称改写v1.txt
│   ├── 写精彩开头v1.txt
│   ├── 开头与正文融合v1.txt
│   ├── 自动精简v1.txt
│   └── 降重改写v1.txt
├── requirements.txt      # 项目依赖库
├── sensitive_words/      # 敏感词词库
│   ├── sw_广告.txt
│   ├── sw_政治.txt
│   └── ...
└── test_novel_list/      # 测试用的小说列表
    ├── 云深不知情浅.txt
    └── ...
```

## 主要模块说明

*   **`adapt_novel_main.py`**: 包含 `AdaptNovel` 类，负责整个小说处理流程的编排。它会初始化小说，将其分段保存，并提供调用 LLM 生成精彩开头、进行第一人称改写等方法。
*   **`novel_adapter.py`**: 提供了 `adapt_novel_by_segments` 函数，该函数负责将小说文本按指定长度分段，并使用多线程方式调用 LLM 进行改写。它支持多次重复改写，并将结果合并保存。
*   **`call_any_llm.py`**: 封装了与 LLM API 交互的通用逻辑，如发送请求、提取响应结果等。
*   **`sensitive_word_detector.py`**: 用于加载敏感词词库并对文本进行检测。

## 使用说明

### 1. 环境配置

确保已安装 Python 环境。然后，在项目根目录下，通过以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

### 2. 准备工作

*   **小说文本**：将需要处理的小说文本文件（例如 `.txt` 格式）准备好。
*   **提示词 (Prompts)**：根据需求，可以在 `prompt` 文件夹下修改或添加新的提示词文件。这些文件定义了 LLM 执行特定任务时的行为。
*   **敏感词词库**：如果需要使用敏感词检测功能，请确保 `sensitive_words` 文件夹下有相应的词库文件。

### 3. 运行示例 (概念性)

具体的运行方式可能需要根据项目入口脚本和参数设计来确定。以下是一个基于现有代码结构的推测性示例：

```python
from adapt_novel.adapt_novel_main import AdaptNovel
from adapt_novel.novel_adapter import adapt_novel_by_segments

# 示例1：初始化小说并生成精彩开头和第一人称版本
novel_name = "我的小说"
# 假设原始小说内容存储在变量 original_novel_content 中
# 或者提供原始小说文件的路径 original_novel_txt_path

# 初始化 AdaptNovel 实例
# adapt_instance = AdaptNovel(novel_name=novel_name, original_novel=original_novel_content)
# 或者
# adapt_instance = AdaptNovel(novel_name=novel_name, original_novel_txt="path/to/your/novel.txt")

# 生成精彩开头
# brilliant_start = adapt_instance.get_brilliant_start()
# print(f"生成的精彩开头：\n{brilliant_start}")

# 生成第一人称小说
# first_person_novel = adapt_instance.get_first_perspective_novel()
# if first_person_novel:
#     print("第一人称小说已生成。")

# 示例2：对小说进行分段改写
# input_novel_path = "novel_result/我的小说/original_novel.txt" # 假设这是原始小说或已处理的某个版本
# adapted_files = adapt_novel_by_segments(novel_file_path=input_novel_path, target_length=1500, repeat_times=1)
# if adapted_files:
#     print(f"小说改写完成，生成文件：{adapted_files}")

# 注意：以上代码仅为示例，实际使用时需要根据项目中 LLM API Key 的配置方式进行相应设置。
# 可能需要在 call_any_llm.py 或相关配置文件中设置 API Key。
```

### 4. 查看结果

处理后的文件将保存在 `novel_result/[小说名称]/` 目录下。

## 依赖库

主要依赖库包括：

*   `openai>=1.0.0`: 用于与 OpenAI 的 LLM API 进行交互。
*   `pypinyin>=0.49.0`: 可能用于中文相关的文本处理（例如，拼音转换，但在当前代码中未直接体现其用途）。

请查看 `requirements.txt` 文件获取完整的依赖列表。

## 注意事项

*   **API Key**：使用此项目需要配置相应的大型语言模型 API Key。请根据 `call_any_llm.py` 或相关模块的实现，在合适的地方配置您的 API Key。
*   **提示词工程**：LLM 的输出质量高度依赖于提示词的设计。您可以根据需要调整 `prompt` 文件夹中的提示词，以获得更佳的改写效果。
*   **文件路径**：代码中部分文件路径可能使用了绝对路径（例如 `novel_adapter.py` 中的 `system_prompt_path`），在不同环境下运行时可能需要调整为相对路径或通过配置传入。
*   **错误处理**：代码中包含了一些基本的错误处理逻辑，但在实际大规模使用时，可能需要进一步完善错误捕获和日志记录机制。

## 未来可改进方向

*   **配置化**：将模型名称、API Key、默认参数等通过配置文件进行管理。
*   **更灵活的 LLM 调用**：支持更多类型的 LLM，并提供更灵活的模型选择机制。
*   **用户界面**：开发一个简单的图形用户界面或Web界面，方便非技术用户使用。
*   **任务队列与异步处理**：对于大量或长篇小说的处理，引入任务队列和更健壮的异步处理机制。
*   **效果评估**：引入文本相似度计算、可读性评估等指标，对改写效果进行量化评估。