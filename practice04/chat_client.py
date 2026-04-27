import os
import json
import time
import http.client
from urllib.parse import urlparse
from datetime import datetime

def load_env():
    """从项目根目录读取.env文件"""
    env_vars = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Error: .env file not found. Please copy env.example to .env and fill in the values.")
        print(f"Looking for .env at: {env_path}")
        exit(1)
    return env_vars

def count_tokens(text):
    """简单的token估算（基于空格分割）"""
    return len(text.split())

def list_directory(directory_path):
    """列出某个目录下的所有文件和文件夹，包括基本属性、大小等信息"""
    try:
        if not os.path.exists(directory_path):
            return f"错误: 目录 '{directory_path}' 不存在"

        if not os.path.isdir(directory_path):
            return f"错误: '{directory_path}' 不是一个目录"

        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                stat_info = os.stat(item_path)
                size = stat_info.st_size
                modified_time = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                if os.path.isdir(item_path):
                    item_type = "目录"
                    size_str = "-"
                else:
                    item_type = "文件"
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.2f} MB"

                items.append({
                    "名称": item,
                    "类型": item_type,
                    "大小": size_str,
                    "修改时间": modified_time
                })
            except Exception as e:
                items.append({
                    "名称": item,
                    "类型": "无法访问",
                    "大小": "-",
                    "修改时间": "-"
                })

        if not items:
            return f"目录 '{directory_path}' 是空的"

        result = f"目录 '{directory_path}' 的内容:\n"
        result += "-" * 60 + "\n"
        result += f"{'名称':<30} {'类型':<10} {'大小':<15} {'修改时间'}\n"
        result += "-" * 60 + "\n"
        for item in items:
            result += f"{item['名称']:<30} {item['类型']:<10} {item['大小']:<15} {item['修改时间']}\n"
        return result
    except Exception as e:
        return f"列出目录时出错: {str(e)}"

def rename_file(directory_path, old_name, new_name):
    """修改某个目录下某个文件的名字"""
    try:
        old_path = os.path.join(directory_path, old_name)
        new_path = os.path.join(directory_path, new_name)

        if not os.path.exists(old_path):
            return f"错误: 文件 '{old_name}' 不存在于目录 '{directory_path}'"

        if os.path.exists(new_path):
            return f"错误: 目标文件名 '{new_name}' 已存在"

        os.rename(old_path, new_path)
        return f"成功: 已将 '{old_name}' 重命名为 '{new_name}'"
    except Exception as e:
        return f"重命名文件时出错: {str(e)}"

def delete_file(directory_path, file_name):
    """删除某个目录下的某个文件"""
    try:
        file_path = os.path.join(directory_path, file_name)

        if not os.path.exists(file_path):
            return f"错误: 文件 '{file_name}' 不存在于目录 '{directory_path}'"

        if os.path.isdir(file_path):
            return f"错误: '{file_name}' 是一个目录，请使用其他方式删除"

        os.remove(file_path)
        return f"成功: 已删除文件 '{file_name}'"
    except Exception as e:
        return f"删除文件时出错: {str(e)}"

def create_file(directory_path, file_name, content):
    """在某个目录下新建一个文件，并且写入内容"""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        file_path = os.path.join(directory_path, file_name)

        if os.path.exists(file_path):
            return f"错误: 文件 '{file_name}' 已存在"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"成功: 已在 '{directory_path}' 创建文件 '{file_name}'"
    except Exception as e:
        return f"创建文件时出错: {str(e)}"

def read_file(directory_path, file_name):
    """读取某个目录下的某个文件的内容"""
    try:
        file_path = os.path.join(directory_path, file_name)

        if not os.path.exists(file_path):
            return f"错误: 文件 '{file_name}' 不存在于目录 '{directory_path}'"

        if os.path.isdir(file_path):
            return f"错误: '{file_name}' 是一个目录，不是文件"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = f"文件 '{file_name}' 的内容:\n"
        result += "=" * 50 + "\n"
        result += content
        result += "\n" + "=" * 50
        return result
    except Exception as e:
        return f"读取文件时出错: {str(e)}"

def curl_fetch(url, method="GET", headers=None, data=None, timeout=30):
    """
    通过curl访问网页并返回网页内容
    参数:
        url (字符串) - 要访问的网页URL
        method (字符串) - HTTP方法，默认GET
        headers (字典) - HTTP请求头
        data (字符串) - POST请求的数据
        timeout (整数) - 超时时间（秒）
    """
    import subprocess
    import shlex

    try:
        # 在Windows上使用curl.exe，确保调用真正的curl命令
        curl_cmd = "curl.exe" if os.name == "nt" else "curl"
        cmd_parts = [curl_cmd, "-s", "-L", "--max-time", str(timeout)]

        if method.upper() != "GET":
            cmd_parts.extend(["-X", method.upper()])

        if headers:
            for key, value in headers.items():
                cmd_parts.extend(["-H", f"{key}: {value}"])

        if data:
            cmd_parts.extend(["-d", data])

        cmd_parts.append(url)

        cmd = " ".join(cmd_parts)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8')

        if result.returncode != 0:
            return f"错误: curl执行失败 - {result.stderr}"

        content = result.stdout
        status_code = "200"  # 简化处理，假设成功

        if not content.strip():
            return f"错误: 获取到的内容为空"

        if len(content) > 5000:
            content = content[:5000] + f"\n... (内容过长，已截断至5000字符)\n"

        result_text = f"网页访问结果:\n"
        result_text += "=" * 50 + "\n"
        result_text += f"URL: {url}\n"
        result_text += "=" * 50 + "\n"
        result_text += content
        result_text += "\n" + "=" * 50
        return result_text
    except subprocess.TimeoutExpired:
        return f"错误: 请求超时（超时时间: {timeout}秒）"
    except Exception as e:
        return f"错误: curl访问失败 - {str(e)}"

def extract_key_information(chat_history, base_url, model, api_key, temperature, max_tokens):
    """从聊天历史中提取关键信息"""
    # 提取最近的聊天记录
    non_system_messages = [msg for msg in chat_history if msg['role'] != 'system']
    if len(non_system_messages) < 2:
        return ""
    
    # 构建提取提示
    extract_prompt = "请从以下聊天记录中提取关键信息，按照5W规则（Who、What、When、Where、Why）进行提取：\n\n"
    for msg in non_system_messages:
        role = "用户" if msg['role'] == "user" else "AI"
        extract_prompt += f"{role}: {msg['content']}\n\n"
    
    # 调用LLM进行提取
    extract_messages = [
        {"role": "system", "content": "你是一个专业的信息提取助手，请从聊天记录中提取关键信息，按照5W规则（Who、What、When、Where、Why）进行提取，每个关键信息单独一行。"},
        {"role": "user", "content": extract_prompt}
    ]
    
    print("\n[正在提取关键信息...]")
    extracted_info = call_llm(extract_messages, base_url, model, api_key, temperature, max_tokens)
    print("[关键信息提取完成]")
    
    return extracted_info

def record_key_information(info):
    """记录关键信息到D:/chat-log/log.txt"""
    log_dir = "D:\chat-log"
    log_file = os.path.join(log_dir, "log.txt")
    
    # 确保目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 追加写入信息
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(info)
        f.write("\n" + "-" * 50 + "\n")
    
    return f"关键信息已记录到: {log_file}"

def search_chat_history(query):
    """查找聊天历史"""
    log_dir = "D:\chat-log"
    log_file = os.path.join(log_dir, "log.txt")
    
    if not os.path.exists(log_file):
        return "错误: 聊天历史记录文件不存在"
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = f"聊天历史记录内容:\n"
    result += "=" * 50 + "\n"
    result += content
    result += "\n" + "=" * 50
    result += f"\n查询内容: {query}"
    
    return result

def anythingllm_query(message):
    """查询AnythingLLM文档仓库"""
    import subprocess
    
    try:
        env = load_env()
        api_key = env.get('ANYTHINGLLM_API_KEY', '')
        workspace_slug = env.get('ANYTHINGLLM_WORKSPACE_SLUG', '')
        
        if not api_key:
            return "错误: ANYTHINGLLM_API_KEY 未在 .env 文件中设置"
        if not workspace_slug:
            return "错误: ANYTHINGLLM_WORKSPACE_SLUG 未在 .env 文件中设置"
        
        url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        data = {
            "message": message
        }
        
        # 构建curl命令
        curl_cmd = "curl.exe" if os.name == "nt" else "curl"
        cmd_parts = [
            curl_cmd,
            "-s",
            "-X", "POST",
            "-H", f"Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
            "-d", json.dumps(data),
            url
        ]
        
        cmd = " ".join(cmd_parts)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8')
        
        if result.returncode != 0:
            return f"错误: curl执行失败 - {result.stderr}"
        
        content = result.stdout
        
        if not content.strip():
            return f"错误: 获取到的内容为空"
        
        # 解析JSON响应
        try:
            response_data = json.loads(content)
            if 'data' in response_data and 'response' in response_data['data']:
                return f"AnythingLLM 响应:\n" + "=" * 50 + "\n" + response_data['data']['response'] + "\n" + "=" * 50
            else:
                return f"错误: 响应格式不正确 - {content}"
        except json.JSONDecodeError:
            return f"错误: 无法解析响应 - {content}"
            
    except subprocess.TimeoutExpired:
        return f"错误: 请求超时（超时时间: 30秒）"
    except Exception as e:
        return f"错误: 查询失败 - {str(e)}"

TOOLS = {
    "list_directory": list_directory,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file": create_file,
    "read_file": read_file,
    "curl_fetch": curl_fetch,
    "search_chat_history": search_chat_history,
    "anythingllm_query": anythingllm_query
}

SYSTEM_PROMPT = """你是一个智能助手，可以通过工具调用来帮助用户完成文件操作任务、网络访问任务和聊天历史查询。

你可以使用以下工具来帮助用户:

1. list_directory(directory_path)
   - 功能: 列出某个目录下的所有文件和文件夹，包括基本属性、大小等信息
   - 参数: directory_path (字符串) - 目录路径

2. rename_file(directory_path, old_name, new_name)
   - 功能: 修改某个目录下某个文件的名字
   - 参数:
     - directory_path (字符串) - 目录路径
     - old_name (字符串) - 原文件名
     - new_name (字符串) - 新文件名

3. delete_file(directory_path, file_name)
   - 功能: 删除某个目录下的某个文件
   - 参数:
     - directory_path (字符串) - 目录路径
     - file_name (字符串) - 要删除的文件名

4. create_file(directory_path, file_name, content)
   - 功能: 在某个目录下新建一个文件，并且写入内容
   - 参数:
     - directory_path (字符串) - 目录路径
     - file_name (字符串) - 文件名
     - content (字符串) - 文件内容

5. read_file(directory_path, file_name)
   - 功能: 读取某个目录下的某个文件的内容
   - 参数:
     - directory_path (字符串) - 目录路径
     - file_name (字符串) - 文件名

6. curl_fetch(url, method, headers, data, timeout)
   - 功能: 通过curl访问网页并返回网页内容
   - 参数:
     - url (字符串) - 要访问的网页URL
     - method (字符串) - HTTP方法，默认GET
     - headers (字典) - HTTP请求头
     - data (字符串) - POST请求的数据
     - timeout (整数) - 超时时间（秒），默认30

7. search_chat_history(query)
   - 功能: 查找聊天历史记录
   - 参数:
     - query (字符串) - 查询内容

8. anythingllm_query(message)
   - 功能: 查询AnythingLLM文档仓库
   - 参数:
     - message (字符串) - 查询消息

当你需要使用工具时，请在回复中包含以下格式的工具调用指令:

[TOOL_CALL]
{
  "name": "函数名",
  "arguments": {
    "参数名": "参数值"
  }
}
[/TOOL_CALL]

请注意:
- 请根据用户需求选择合适的工具
- 如果需要多个工具调用，可以依次调用
- 在执行文件操作前，请确保路径和文件名正确
- 请友好地回复用户，解释你正在做什么
- 当用户发送的信息以"/search"开头，或用户表达了"查找聊天历史"的意思时，请使用search_chat_history工具
- 当用户提到"文档仓库"、"文件仓库"、"仓库"时，请使用anythingllm_query工具"""

def parse_tool_calls(response_text):
    """从LLM响应中解析工具调用"""
    tool_calls = []
    start_tag = "[TOOL_CALL]"
    end_tag = "[/TOOL_CALL]"

    start_idx = response_text.find(start_tag)
    while start_idx != -1:
        end_idx = response_text.find(end_tag, start_idx)
        if end_idx == -1:
            break

        tool_json = response_text[start_idx + len(start_tag):end_idx].strip()
        try:
            tool_data = json.loads(tool_json)
            tool_calls.append(tool_data)
        except json.JSONDecodeError:
            pass

        start_idx = response_text.find(start_tag, end_idx)

    return tool_calls

def execute_tool_call(tool_call):
    """执行单个工具调用"""
    tool_name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})

    if tool_name not in TOOLS:
        return f"错误: 未知的工具 '{tool_name}'"

    try:
        func = TOOLS[tool_name]
        return func(**arguments)
    except Exception as e:
        return f"执行工具 '{tool_name}' 时出错: {str(e)}"

def call_llm(messages, base_url, model, api_key, temperature, max_tokens):
    """调用LLM API"""
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    is_https = parsed_url.scheme == 'https'

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    if is_https:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    try:
        conn.request('POST', f"{path}/chat/completions", json.dumps(data), headers)
        response = conn.getresponse()

        full_response = ""
        for line in response:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_line = line[6:].strip()
                if data_line == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content = delta['content']
                            print(content, end='', flush=True)
                            full_response += content
                except json.JSONDecodeError:
                    pass
        print()
        return full_response
    except Exception as e:
        print(f"Error connecting to LLM: {e}")
        return ""
    finally:
        conn.close()

def get_chat_history_length(chat_history):
    """计算聊天历史的总长度"""
    total_length = 0
    for message in chat_history:
        if message['role'] != 'system':  # 不计算系统提示词
            total_length += len(message['content'])
    return total_length

def summarize_chat_history(chat_history, base_url, model, api_key, temperature, max_tokens):
    """总结聊天历史"""
    # 提取需要总结的部分（前70%）
    non_system_messages = [msg for msg in chat_history if msg['role'] != 'system']
    if len(non_system_messages) <= 2:
        return chat_history
    
    # 计算分割点
    split_point = int(len(non_system_messages) * 0.7)
    messages_to_summarize = non_system_messages[:split_point]
    messages_to_keep = non_system_messages[split_point:]
    
    # 构建总结提示
    summary_prompt = "请总结以下聊天记录，保持关键信息和对话脉络：\n\n"
    for msg in messages_to_summarize:
        role = "用户" if msg['role'] == "user" else "AI"
        summary_prompt += f"{role}: {msg['content']}\n\n"
    
    # 调用LLM进行总结
    summary_messages = [
        {"role": "system", "content": "你是一个专业的对话总结助手，请简洁明了地总结对话内容。"},
        {"role": "user", "content": summary_prompt}
    ]
    
    print("\n[正在总结聊天历史...]")
    summary = call_llm(summary_messages, base_url, model, api_key, temperature, max_tokens)
    
    # 构建新的聊天历史
    new_chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": f"[聊天历史总结]\n{summary}"}
    ]
    
    # 添加保留的消息
    new_chat_history.extend(messages_to_keep)
    
    print("[聊天历史总结完成]")
    return new_chat_history

def main():
    env = load_env()

    base_url = env.get('BASE_URL', 'http://localhost:1234/v1')
    model = env.get('MODEL', '')
    api_key = env.get('API_KEY', 'lm-studio')
    temperature = float(env.get('TEMPERATURE', 0.7))
    max_tokens = int(env.get('MAX_TOKENS', 1000))

    print("=" * 60)
    print("       AI 智能助手 - 增强版")
    print("=" * 60)
    print(f"模型: {model}")
    print(f"服务器: {base_url}")
    print("可用工具: 列出目录、重命名文件、删除文件、创建文件、读取文件、查找聊天历史、查询文档仓库")
    print("提示: 输入消息开始聊天，按 Ctrl+C 退出")
    print("=" * 60)

    chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    chat_count = 0

    try:
        while True:
            user_input = input("\n你: ")

            if user_input.lower() in ['exit', 'quit', '退出']:
                print("\n退出聊天...")
                break

            chat_history.append({"role": "user", "content": user_input})
            chat_count += 1

            # 检查是否需要压缩聊天历史
            non_system_messages = [msg for msg in chat_history if msg['role'] != 'system']
            chat_length = get_chat_history_length(chat_history)
            
            if len(non_system_messages) > 10 or chat_length > 3000:  # 超过5轮对话（每轮包含用户和AI消息）或长度超过3k
                chat_history = summarize_chat_history(chat_history, base_url, model, api_key, temperature, max_tokens)

            # 每五次聊天提取一次关键信息
            if chat_count % 5 == 0:
                key_info = extract_key_information(chat_history, base_url, model, api_key, temperature, max_tokens)
                if key_info:
                    record_result = record_key_information(key_info)
                    print(f"\n{record_result}")

            max_iterations = 10
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                print("\nAI: ", end='', flush=True)
                start_time = time.time()

                response_text = call_llm(
                    chat_history,
                    base_url,
                    model,
                    api_key,
                    temperature,
                    max_tokens
                )

                end_time = time.time()

                if not response_text:
                    break

                chat_history.append({"role": "assistant", "content": response_text})

                tool_calls = parse_tool_calls(response_text)

                if not tool_calls:
                    time_taken = end_time - start_time
                    tokens = count_tokens(response_text)
                    print(f"\n[{time_taken:.2f}秒, {tokens} tokens]")
                    break

                for tool_call in tool_calls:
                    print(f"\n[正在执行工具: {tool_call.get('name')}]")
                    result = execute_tool_call(tool_call)
                    print(f"[工具执行结果]\n{result}")

                    tool_result_message = f"工具执行结果:\n{result}"
                    chat_history.append({"role": "user", "content": tool_result_message})

            print("\n" + "-" * 60)

    except KeyboardInterrupt:
        print("\n\n退出聊天...")
        print("=" * 60)

        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
        print(f"聊天历史已保存到: {history_file}")
        print("=" * 60)

if __name__ == "__main__":
    main()