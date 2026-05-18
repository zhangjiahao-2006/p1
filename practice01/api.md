# AI聊天客户端API接口说明

## 1. 内部函数接口

### 1.1 load_env()

**功能**：从项目根目录读取.env配置文件

**参数**：无

**返回值**：
- `dict` - 环境变量字典，包含以下键：
  - `BASE_URL`: str - LLM API基础URL
  - `MODEL`: str - 模型名称
  - `API_KEY`: str - API密钥
  - `TEMPERATURE`: str - 温度参数
  - `MAX_TOKENS`: str - 最大token数

**异常处理**：
- 文件不存在时打印错误信息并退出程序

**调用示例**：
```python
env = load_env()
base_url = env.get('BASE_URL', 'http://localhost:1234/v1')
```

---

### 1.2 count_tokens(text)

**功能**：简单估算文本的token数量（基于空格分割）

**参数**：
- `text`: str - 要计算的文本内容

**返回值**：
- `int` - 估算的token数量

**调用示例**：
```python
tokens = count_tokens("Hello, how are you?")
```

---

### 1.3 call_llm(messages, base_url, model, api_key, temperature, max_tokens)

**功能**：调用LLM API进行聊天完成

**参数**：
| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| messages | List[dict] | 消息历史列表，每个元素包含role和content |
| base_url | str | LLM API基础URL |
| model | str | 模型名称 |
| api_key | str | API密钥 |
| temperature | float | 温度参数（0-1） |
| max_tokens | int | 最大响应token数 |

**返回值**：
- `str` - AI的完整响应内容

**实现细节**：
1. 解析base_url获取host、path和协议类型
2. 构建HTTP/HTTPS连接
3. 发送POST请求到 `/chat/completions`
4. 流式接收响应，逐块打印
5. 累积响应内容并返回

**调用示例**：
```python
messages = [
    {"role": "system", "content": "你是一个AI助手"},
    {"role": "user", "content": "你好"}
]
response = call_llm(messages, "http://localhost:1234/v1", "model-name", "api-key", 0.7, 1000)
```

---

### 1.4 main()

**功能**：主函数，启动聊天客户端

**参数**：无

**返回值**：无

**执行流程**：
1. 加载环境配置
2. 初始化聊天历史（包含系统提示词）
3. 显示欢迎界面
4. 进入主循环：
   - 等待用户输入
   - 添加用户消息到历史
   - 调用LLM API
   - 流式输出响应
   - 添加AI响应到历史
   - 显示统计信息
5. 捕获KeyboardInterrupt退出
6. 保存聊天历史到JSON文件

---

## 2. 外部API接口（LLM服务）

### 2.1 聊天完成接口

**端点**：`POST /chat/completions`

**请求头**：
```
Content-Type: application/json
Authorization: Bearer {api_key}
```

**请求体**：
```json
{
    "model": "string",
    "messages": [
        {
            "role": "string",
            "content": "string"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": true
}
```

**请求参数说明**：
| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| model | string | 是 | 模型名称 |
| messages | array | 是 | 消息历史列表 |
| messages[].role | string | 是 | 角色：system/user/assistant |
| messages[].content | string | 是 | 消息内容 |
| temperature | float | 否 | 温度参数，默认0.7 |
| max_tokens | int | 否 | 最大token数，默认1000 |
| stream | bool | 否 | 是否流式响应，默认true |

**响应格式**（流式）：
```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":xxx,"model":"xxx","choices":[{"delta":{"content":"你"},"index":0}]}
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":xxx,"model":"xxx","choices":[{"delta":{"content":"好"},"index":0}]}
data: [DONE]
```

**响应字段说明**：
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | string | 请求ID |
| object | string | 对象类型 |
| created | int | 创建时间戳 |
| model | string | 模型名称 |
| choices | array | 选择列表 |
| choices[].delta | object | 增量内容 |
| choices[].delta.content | string | 响应片段 |
| choices[].index | int | 选择索引 |

---

## 3. 数据结构

### 3.1 聊天消息

```python
{
    "role": "system" | "user" | "assistant",
    "content": "消息内容"
}
```

### 3.2 环境配置

```python
{
    "BASE_URL": "http://localhost:1234/v1",
    "MODEL": "your-model-name",
    "API_KEY": "lm-studio",
    "TEMPERATURE": "0.7",
    "MAX_TOKENS": "1000"
}
```

### 3.3 聊天历史文件（chat_history.json）

```json
[
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户消息1"},
    {"role": "assistant", "content": "AI响应1"},
    {"role": "user", "content": "用户消息2"},
    {"role": "assistant", "content": "AI响应2"}
]
```