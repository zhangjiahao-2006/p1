import subprocess
import time

# 启动chat_client.py进程
process = subprocess.Popen(
    ['python', 'chat_client.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd='f:\\models\\aizuoye\\p1\\practice02'
)

# 等待启动完成
time.sleep(2)

# 发送请求
request = "请帮我获取成都的天气预报，使用curl访问 https://wttr.in/成都，然后告诉我明天成都的最高和最低气温\n"
process.stdin.write(request)
process.stdin.flush()

# 读取输出
try:
    output = process.stdout.read(20000)  # 读取足够的输出
    print(output)
except Exception as e:
    print(f"Error reading output: {e}")
finally:
    process.terminate()