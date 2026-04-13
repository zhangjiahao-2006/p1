import os
import json
import time
import http.client
from urllib.parse import urlparse

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

def call_llm_stream(messages, base_url, model, api_key, temperature, max_tokens):
    """流式调用LLM"""
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
        print()  # 换行
        return full_response
    except Exception as e:
        print(f"Error connecting to LLM: {e}")
        print("Please make sure LMStudio is running and the server is started.")
        return ""
    finally:
        conn.close()

def main():
    env = load_env()
    
    base_url = env.get('BASE_URL', 'http://localhost:1234/v1')
    model = env.get('MODEL', '')
    api_key = env.get('API_KEY', 'lm-studio')
    temperature = float(env.get('TEMPERATURE', 0.7))
    max_tokens = int(env.get('MAX_TOKENS', 1000))
    
    print("=" * 60)
    print("       AI 智能体终端聊天界面")
    print("=" * 60)
    print(f"模型: {model}")
    print(f"服务器: {base_url}")
    print("提示: 输入消息开始聊天，按 Ctrl+C 退出")
    print("=" * 60)
    
    # 初始化聊天历史
    chat_history = []
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n你: ")
            
            # 添加用户消息到历史记录
            chat_history.append({"role": "user", "content": user_input})
            
            # 限制历史记录长度（防止token过多）
            if len(chat_history) > 10:
                chat_history = chat_history[-10:]
            
            # 发送请求并流式接收响应
            print("AI: ", end='', flush=True)
            start_time = time.time()
            
            response_text = call_llm_stream(
                chat_history,
                base_url,
                model,
                api_key,
                temperature,
                max_tokens
            )
            
            end_time = time.time()
            
            # 添加AI响应到历史记录
            if response_text:
                chat_history.append({"role": "assistant", "content": response_text})
                
                # 统计性能
                input_tokens = count_tokens(user_input)
                output_tokens = count_tokens(response_text)
                total_tokens = input_tokens + output_tokens
                time_taken = end_time - start_time
                tokens_per_second = total_tokens / time_taken if time_taken > 0 else 0
                
                print(f"\n[{time_taken:.2f}秒, {total_tokens} tokens, {tokens_per_second:.2f} tokens/s]")
    
    except KeyboardInterrupt:
        print("\n\n退出聊天...")
        print("=" * 60)
        
        # 保存聊天历史到文件
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
        print(f"聊天历史已保存到: {history_file}")
        print("=" * 60)

if __name__ == "__main__":
    main()
