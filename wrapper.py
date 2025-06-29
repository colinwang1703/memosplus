from openai import OpenAI
from collections import deque

from config import Config

class ModelWrapper:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.ai_api_key, 
            base_url=config.ai_base,
        )

    def get(self, messages, temperature=0.3):
        # 支持直接传入字符串，将其封装为用户消息列表
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        completion = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=messages,
            temperature=temperature,
        )
        return completion.choices[0].message.content

    def init_chat(self, history={"role": "system", "content": ""}, max_len=10):
        """
        初始化对话队列，history 为首条系统消息，max_len 为最大消息条数
        """
        self.history = deque([history], maxlen=max_len)

    def chat(self, query, temperature=0.3):
        # 将用户消息加入队列（超过 maxlen 自动丢弃最旧消息）
        self.history.append({"role": "user", "content": query})
        completion = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=list(self.history),
            temperature=temperature,
        )
        result = completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": result})
        return result