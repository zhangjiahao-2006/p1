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

def call_llm():
    env = load_env()
    
    base_url = env.get('BASE_URL', 'http://localhost:1234/v1')
    model = env.get('MODEL', '')
    api_key = env.get('API_KEY', 'lm-studio')
    temperature = float(env.get('TEMPERATURE', 0.7))
    max_tokens = int(env.get('MAX_TOKENS', 1000))
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    is_https = parsed_url.scheme == 'https'
    
    prompt = "Hello, how are you?"
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    input_tokens = count_tokens(prompt)
    
    start_time = time.time()
    
    if is_https:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', f"{path}/chat/completions", json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error connecting to LLM: {e}")
        print("Please make sure LMStudio is running and the server is started.")
        exit(1)
    finally:
        conn.close()
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    if 'choices' in response_data and len(response_data['choices']) > 0:
        response_text = response_data['choices'][0]['message']['content']
        output_tokens = count_tokens(response_text)
        total_tokens = input_tokens + output_tokens
        
        tokens_per_second = total_tokens / time_taken if time_taken > 0 else 0
        
        print("=" * 50)
        print("         LLM 调用性能统计")
        print("=" * 50)
        print(f"模型: {model}")
        print(f"输入: {prompt}")
        print("\n--- 统计信息 ---")
        print(f"输入 tokens: {input_tokens}")
        print(f"输出 tokens: {output_tokens}")
        print(f"总 tokens:   {total_tokens}")
        print(f"耗时:        {time_taken:.2f} 秒")
        print(f"速度:        {tokens_per_second:.2f} tokens/秒")
        print("\n--- 响应 ---")
        print(response_text)
        print("=" * 50)
    else:
        print("响应错误:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    call_llm()
