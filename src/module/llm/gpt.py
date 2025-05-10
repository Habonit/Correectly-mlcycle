from openai import OpenAI
import os
from dotenv import load_dotenv
from copy import deepcopy
from datetime import datetime
import argparse
from loguru import logger
from typing import Union

load_dotenv()

class GPTClient:
    ALLOWED_MODELS = ("gpt-4o-mini", "gpt-4.1-nano", "gpt-4.1-mini")
    
    def __init__(self, 
                 model: str="gpt-4o-mini", 
                 system_prompt: str="당신은 친절한 인공지능 비서입니다.",
                 ):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            message = "Environment variable OPENAI_API_KEY is not set"
            logger.error(message)
            raise ValueError(message)
        OpenAI.api_key = api_key
    
        # 모델 검증
        if model not in self.ALLOWED_MODELS:
            message = f"Invalid model: '{model}'. Choose from {self.ALLOWED_MODELS}"
            logger.error(message)
            raise ValueError(message)
        self.model = model

        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.messages = []
        self.messages.append({"role":"system", "content":system_prompt})
        self.input_tokens = 0
        self.output_tokens = 0
        self.counter = 0
        self.raw_messages = []
        
        self.temperature = 0.7
        self.top_p = 0.9
        self.max_tokens = 200

        logger.debug(f"Model: {self.model}")
        logger.debug(f"System Prompt: {self.system_prompt}")
        
    def _extract_content(self, response):
        return response.choices[0].message.content
    
    def _apply_request(self, messages: list, temporary: bool, **gen_params):
        start_time = datetime.now()
        default_params = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
        
        for key, value in gen_params.items():
            if key in default_params and value is not None:
                default_params[key] = value
                
        params = {
            "model": self.model,
            "messages": messages,
        }
        
        for key, value in default_params.items():
            if value is not None:
                params[key] = value
                
        logger.debug(f"[Apply Request] Generation Params: {params}")
        
        try:
            response = self.client.chat.completions.create(**params)
        except Exception as e:
            logger.error(f"[Apply Request] OpenAI API request failed: {e}")
            raise

        logger.debug(f"[Apply Request] Raw Output: {response}")
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        assistant_message = self._extract_content(response)
        
        logger.info(f"[Apply Request] Assistant: {assistant_message}")
        logger.debug(
            f"[Apply Request] Tokens - input: {input_tokens}, output: {output_tokens}, total: {input_tokens + output_tokens}"
        )

        if not temporary:
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens

            self.raw_messages.append({
                "id": self.counter,
                "request": deepcopy(messages),
                "response": response.model_dump()
            })
            self.counter += 1
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"[Apply Request] Elapsed Time: {duration}")
        
        return {
            "message": assistant_message,
            "duration": duration,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
        
    def send_soft_temporary_message(self, user_message: str, **gen_params) -> dict[str, Union[str,int,float]]:
        messages = deepcopy(self.messages)
        messages.append({"role":"user", "content":user_message})
        response = self._apply_request(messages, temporary=True, **gen_params)

        return response
    
    def send_hard_temporary_message(self, user_message: str, **gen_params) -> dict[str, Union[str,int,float]]:
        messages = []
        messages.append({"role":"system", "content":self.system_prompt})
        messages.append({"role":"user", "content":user_message})
        response = self._apply_request(messages, temporary=True, **gen_params)
        
        return response
    
    def send_message(self, user_message: str, **gen_params) -> dict[str, Union[str,int,float]]:
        self.messages.append({"role":"user", "content":user_message})
        response = self._apply_request(self.messages, temporary=False, **gen_params)
        self.messages.append({"role":"assistant", "content":response['message']})
        
        return response
    
    def export_history(self):
        return self.messages
    
    def export_raw_history(self):
        return self.raw_messages
    
    def get_system_prompt(self):
        return self.system_prompt
    
    def get_model(self):
        return self.model
    
    def get_tokens(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

if __name__ == "__main__":
    """
    python -m module.llm.gpt
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    system_prompt = "당신은 인공지능을 가르치는 교수님입니다."
    gpt = GPTClient(system_prompt=system_prompt)

    question = "attention에 대해 설명해주세요."
    print(f"질문 1: {question}")
    res = gpt.send_message(question)
    print("GPT 응답 1:\n", res, "\n")
    print(gpt.get_tokens())
    
    print("전체 대화 기록 (export_history):")
    for msg in gpt.export_history():
        print(f"[{msg['role'].upper()}] {msg['content']}\n")
