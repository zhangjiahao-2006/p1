import os
import time
import json
import http.client
from urllib.parse import urlparse
import subprocess

# 读取 .env 文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        print(f"❌ 错误: .env 文件不存在，请放在当前脚本同一文件夹下")
        return None
    
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

# ====================== 工具函数 ======================
def list_files(directory):
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_info = {
                    "name": item,
                    "size": os.path.getsize(item_path),
                    "last_modified": os.path.getmtime(item_path),
                    "is_file": True
                }
            else:
                file_info = {"name": item, "is_file": False}
            files.append(file_info)
        return json.dumps({"success": True, "files": files}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return json.dumps({"success": True, "message": f"文件已重命名为 {new_name}"}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "error": "文件不存在"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

def delete_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return json.dumps({"success": True, "message": "文件已删除"}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "error": "文件不存在"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

def create_file(directory, file_name, content=""):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return json.dumps({"success": True, "message": f"文件 {file_name} 已创建成功"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

def read_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return json.dumps({"success": True, "content": content}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "error": "文件不存在"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

def curl_request(url):
    try:
        result = subprocess.run(['curl', '-s', url], capture_output=True, timeout=30)
        if result.returncode == 0:
            try:
                content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                content = result.stdout.decode('gbk', errors='replace')
            return json.dumps({"success": True, "content": content}, ensure_ascii=False)
        else:
            try:
                error = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                error = result.stderr.decode('gbk', errors='replace')
            return json.dumps({"success": False, "error": error}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

# ====================== 搜索聊天历史 ======================
def search_chat_history(query):
    try:
        log_dir = r"D:\chat-log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, "log.txt")
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# 聊天历史关键信息\n")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return json.dumps({"success": True, "content": content, "query": query}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

# ====================== 工具定义 ======================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录下的所有文件和文件夹",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要列出的目录路径，例如 D:\\test"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "在指定目录下创建一个新文件并写入内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "要创建的文件名，例如 test.txt"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入文件的内容，默认为空字符串",
                        "default": ""
                    }
                },
                "required": ["directory", "file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除指定目录下的指定文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "要删除的文件名"
                    }
                },
                "required": ["directory", "file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "重命名指定目录下的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "old_name": {
                        "type": "string",
                        "description": "原文件名"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "新文件名"
                    }
                },
                "required": ["directory", "old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定目录下文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "要读取的文件名"
                    }
                },
                "required": ["directory", "file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "curl_request",
            "description": "访问指定的网页URL并返回内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要访问的网页URL，例如 https://www.baidu.com"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_chat_history",
            "description": "搜索聊天历史记录，当用户需要查找聊天历史时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户的搜索查询，例如 '查找关于文件操作的记录'"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ====================== 通义千问专属系统提示词（最高优先级） ======================
# 注意：必须用user角色发送，通义千问会忽略system角色
def build_system_prompt(user_info):
    return f"""【最高优先级规则，必须严格遵守，违反任何一条都算错误】
1.  绝对禁止提及"通义千问"、"阿里巴巴"、"我是AI助手"这类身份信息
2.  必须100%记住用户的所有身份信息：{user_info}
3.  回答必须完全贴合用户的问题，不能答非所问，不能输出无关内容
4.  工具调用仅在后台执行，绝对不能在回复中提及任何工具相关内容
5.  当用户询问自己的身份、名字时，必须准确回答，不能反问
6.  保持回答简洁、准确，符合用户的提问意图

现在请回答用户的问题："""

# ====================== 流式调用（通义千问专属适配） ======================
def call_llm_stream(env_vars, messages, user_info, is_tool_round=False):
    start_time = time.time()
    url = urlparse(env_vars['BASE_URL'])
    host = url.netloc
    path = "/v1/chat/completions"

    # 通义千问专属：把系统提示词放到第一条user消息
    system_msg = {"role": "user", "content": build_system_prompt(user_info)}
    final_messages = [system_msg] + messages

    data = {
        "model": env_vars["MODEL"],
        "messages": final_messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0.1,  # 极低温度，强制模型听话
        "max_tokens": int(env_vars.get("MAX_TOKENS", 2048)),
        "stream": True
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {env_vars.get('API_KEY', '')}"
    }

    timeout = int(env_vars.get('TIMEOUT', '120'))
    if url.scheme == 'https':
        conn = http.client.HTTPSConnection(host, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(host, timeout=timeout)

    full_content = ""
    tool_calls = []

    try:
        conn.request("POST", path, json.dumps(data), headers)
        response = conn.getresponse()

        # 工具调用轮次完全不打印任何内容
        if not is_tool_round:
            print("🤖 AI 正在思考...", end="", flush=True)

        for line in response.fp:
            line = line.decode("utf-8").strip()
            if not line: continue
            if line.startswith("data: "):
                data_part = line[6:]
                if data_part == "[DONE]": break
                try:
                    jd = json.loads(data_part)
                    delta = jd["choices"][0]["delta"]
                    
                    # 仅在非工具调用轮次、有实际内容时打印
                    if not is_tool_round and "content" in delta and delta["content"]:
                        token = delta["content"]
                        full_content += token
                        if not tool_calls:
                            if not full_content or len(full_content) == len(token):
                                print("\r" + " " * 20 + "\r", end="", flush=True)
                                print("🤖 AI 回复：", end="", flush=True)
                            print(token, end="", flush=True)
                    
                    # 通义千问专属工具调用拼接
                    if "tool_calls" in delta and delta["tool_calls"]:
                        for tc in delta["tool_calls"]:
                            index = tc["index"]
                            if index >= len(tool_calls):
                                tool_calls.append({
                                    "id": tc.get("id", ""),
                                    "type": "function",
                                    "function": {
                                        "name": "",
                                        "arguments": ""
                                    }
                                })
                            if "function" in tc:
                                if "name" in tc["function"]:
                                    tool_calls[index]["function"]["name"] += tc["function"]["name"]
                                if "arguments" in tc["function"]:
                                    tool_calls[index]["function"]["arguments"] += tc["function"]["arguments"]
                except:
                    continue

        if not is_tool_round:
            print("\n")
    except Exception as e:
        print(f"\n❌ 连接失败：{str(e)}")
        return None, None, 0, 0, 0
    finally:
        conn.close()

    duration = time.time() - start_time
    total_tokens = len(full_content) // 3
    speed = total_tokens / duration if duration > 0 else 0

    return full_content, tool_calls, total_tokens, duration, speed

# ====================== 自动提取用户身份信息（每轮都执行） ======================
def extract_user_info(messages):
    user_info = []
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            # 提取身份关键词
            if "我是" in content:
                user_info.append(content.split("我是", 1)[1].strip())
            elif "我叫" in content:
                user_info.append(content.split("我叫", 1)[1].strip())
    
    # 合并去重
    user_info = list(set(user_info))
    if not user_info:
        return "普通用户"
    return "，".join(user_info)

# ====================== 保存关键信息到log.txt（每轮都保存） ======================
def save_key_information(user_question, ai_answer, user_info):
    log_dir = r"D:\chat-log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "log.txt")
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("# 聊天历史关键信息\n")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"用户身份：{user_info}\n")
        f.write(f"用户提问：{user_question}\n")
        f.write(f"AI回答：{ai_answer}\n")

# ====================== 聊天历史压缩（保留最近10轮完整消息） ======================
def compress_chat_history(messages):
    if len(messages) <= 10:
        return messages
    
    print("\n📝 检测到聊天历史过长，开始压缩...")
    # 保留最近10轮完整消息，更早的压缩成摘要
    messages_to_keep = messages[-10:]
    print("✅ 聊天历史压缩完成")
    return messages_to_keep

# ====================== 主循环 ======================
def main():
    env_vars = load_env()
    if not env_vars: return

    print("=" * 50)
    print("✅ 通义千问专属工具助手已启动")
    print(f"模型：{env_vars['MODEL']}")
    print(f"地址：{env_vars['BASE_URL']}")
    print("=" * 50)

    messages = []
    user_info = "普通用户"

    while True:
        prompt = input("\n请输入问题（输入 exit 退出）：")
        if prompt.lower() == "exit": break

        messages.append({"role": "user", "content": prompt})
        
        # 每轮自动提取用户身份信息
        current_user_info = extract_user_info(messages)
        if current_user_info != "普通用户":
            user_info = current_user_info
        
        # 压缩聊天历史
        messages = compress_chat_history(messages)

        while True:
            # 标记工具调用轮次
            is_tool_round = any(msg.get("tool_calls") for msg in messages[-2:])
            content, tool_calls, total, duration, speed = call_llm_stream(env_vars, messages, user_info, is_tool_round)

            if not content and not tool_calls:
                break

            if tool_calls:
                # 后台执行工具，完全不显示
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    try:
                        params = json.loads(tc["function"]["arguments"])
                    except:
                        params = {}
                    
                    if tool_name == "list_files":
                        res = list_files(params.get("directory"))
                    elif tool_name == "rename_file":
                        res = rename_file(params.get("directory"), params.get("old_name"), params.get("new_name"))
                    elif tool_name == "delete_file":
                        res = delete_file(params.get("directory"), params.get("file_name"))
                    elif tool_name == "create_file":
                        res = create_file(params.get("directory"), params.get("file_name"), params.get("content", ""))
                    elif tool_name == "read_file":
                        res = read_file(params.get("directory"), params.get("file_name"))
                    elif tool_name == "curl_request":
                        res = curl_request(params.get("url"))
                    elif tool_name == "search_chat_history":
                        res = search_chat_history(params.get("query"))
                    else:
                        res = json.dumps({"success": False, "error": "未知工具"}, ensure_ascii=False)
                    
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [tc]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tool_name,
                        "content": res
                    })

                continue

            # 保存到log.txt
            save_key_information(prompt, content, user_info)
            
            messages.append({"role": "assistant", "content": content})
            
            print("=" * 50)
            print(f"⏱ 耗时：{duration:.2f}s  |  📊 Tokens：{total}  |  ⚡ 速度：{speed:.2f} token/s")
            print("=" * 50)
            break

if __name__ == "__main__":
    main()