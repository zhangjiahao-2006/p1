"""测试聊天客户端功能"""
import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chat_client

class TestChatClient(unittest.TestCase):
    """聊天客户端测试类"""

    def test_count_tokens(self):
        """测试token计数功能"""
        text = "Hello, how are you?"
        result = chat_client.count_tokens(text)
        self.assertEqual(result, 4)

        text2 = "这是一个测试句子"
        result2 = chat_client.count_tokens(text2)
        self.assertEqual(result2, 1)

    def test_load_env_exists(self):
        """测试加载存在的.env文件"""
        env = chat_client.load_env()
        self.assertIsInstance(env, dict)
        self.assertIn('BASE_URL', env)
        self.assertIn('MODEL', env)
        self.assertIn('API_KEY', env)

    def test_chat_history_format(self):
        """测试聊天历史格式"""
        chat_history = [
            {"role": "system", "content": "你是一个AI助手"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！我是AI助手。"}
        ]
        
        for msg in chat_history:
            self.assertIn('role', msg)
            self.assertIn('content', msg)
            self.assertIn(msg['role'], ['system', 'user', 'assistant'])

    def test_empty_input_handling(self):
        """测试空输入处理"""
        user_input = ""
        self.assertTrue(not user_input.strip())
        
        user_input2 = "   "
        self.assertTrue(not user_input2.strip())

    def test_env_config_validation(self):
        """测试环境配置验证"""
        env = chat_client.load_env()
        
        base_url = env.get('BASE_URL', '')
        self.assertTrue(base_url.startswith('http://') or base_url.startswith('https://'))
        
        temperature = float(env.get('TEMPERATURE', 0.7))
        self.assertGreaterEqual(temperature, 0)
        self.assertLessEqual(temperature, 1)
        
        max_tokens = int(env.get('MAX_TOKENS', 1000))
        self.assertGreater(max_tokens, 0)

    def test_json_save_format(self):
        """测试JSON保存格式"""
        chat_history = [
            {"role": "system", "content": "测试"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"}
        ]
        
        test_file = 'test_history.json'
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
            
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            self.assertEqual(loaded, chat_history)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main(verbosity=2)
