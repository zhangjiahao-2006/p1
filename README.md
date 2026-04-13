# AI智能体开发教学项目

## 项目概述

这是一个基于Python的AI智能体开发教学项目，旨在帮助学习者了解如何使用Python标准库与本地LLM（大型语言模型）进行交互。

## 项目结构

```
├── practice01/           # 练习目录
│   └── llm_client.py     # LLM客户端代码
├── venv/                 # 虚拟环境
├── .env                  # 环境配置文件
├── env.example           # 环境配置模板
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明文档
```

## Python代码功能说明

### practice01/llm_client.py

**功能用途：**
- 调用本地LLM（LMStudio）服务器
- 发送聊天完成请求
- 接收和处理LLM响应
- 统计性能指标（token消耗、时间、速度）
- 友好的中文输出界面

**核心功能模块：**

1. **load_env()**
   - 从项目根目录读取.env配置文件
   - 解析环境变量
   - 处理文件不存在的错误

2. **count_tokens()**
   - 简单的token估算（基于空格分割）
   - 用于统计输入和输出的token数量

3. **call_llm()**
   - 主函数，协调整个LLM调用流程
   - 解析配置参数
   - 构建HTTP请求
   - 发送请求并接收响应
   - 计算性能指标
   - 格式化输出结果

**技术实现：**
- 使用Python标准库 `http.client` 进行HTTP/HTTPS请求
- 使用 `json` 模块处理JSON数据
- 使用 `time` 模块进行时间统计
- 使用 `os` 模块处理文件路径
- 使用 `urllib.parse` 解析URL

## 教学目标

1. **基础Python编程**
   - 函数定义和调用
   - 文件操作
   - 异常处理
   - 命令行输出格式化

2. **HTTP/HTTPS通信**
   - 了解HTTP请求结构
   - 学习如何使用标准库发送POST请求
   - 理解请求头和请求体的构建

3. **环境配置管理**
   - 学习如何使用.env文件管理配置
   - 理解环境变量的重要性和使用方法

4. **LLM API交互**
   - 了解OpenAI兼容的API接口
   - 学习如何构建聊天完成请求
   - 理解API响应格式

5. **性能分析**
   - 学习如何统计和分析性能指标
   - 理解token消耗、响应时间等概念

6. **项目结构组织**
   - 学习如何组织Python项目
   - 理解虚拟环境的使用
   - 了解.gitignore文件的作用

## 环境配置

1. **安装Python 3.12+**
2. **安装LMStudio**并下载一个LLM模型
3. **启动LMStudio本地服务器**（默认端口1234）
4. **复制配置文件**：
   ```bash
   copy env.example .env
   ```
5. **编辑.env文件**，填写模型名称

## 运行项目

```bash
# 使用系统Python
py practice01\llm_client.py

# 或使用虚拟环境Python
venv\Scripts\python.exe practice01\llm_client.py
```

## 预期输出

运行后，你将看到类似以下的输出：

```
==================================================
         LLM 调用性能统计
==================================================
模型: your-model-name
输入: Hello, how are you?

--- 统计信息 ---
输入 tokens: 4
输出 tokens: 20
总 tokens:   24
耗时:        1.23 秒
速度:        19.51 tokens/秒

--- 响应 ---
I'm doing well, thank you! How can I assist you today?
==================================================
```

## 扩展学习

- 尝试修改prompt内容，观察不同输入的响应
- 调整temperature参数，观察生成结果的变化
- 尝试连接其他OpenAI兼容的LLM服务
- 扩展代码，添加更多功能（如对话历史管理）

## 注意事项

- 确保LMStudio服务器正在运行
- 确保.env文件中的配置正确
- 部分模型可能需要较长的响应时间
- token估算仅为基于空格的简单计算，实际token数可能有所不同
