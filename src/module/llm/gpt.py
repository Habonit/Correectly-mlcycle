from openai import OpenAI
import os
from dotenv import load_dotenv
from copy import deepcopy
from typing import Literal
import argparse
from src.utils.logger import setup_logger

load_dotenv()

class GPTClient:
    def __init__(self, 
                 model: Literal["gpt-4o-mini","gpt-4.1-nano","gpt-4.1-mini"]="gpt-4o-mini", 
                 system_prompt: str="당신은 친절한 인공지능 비서입니다.",
                 log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]="INFO"
                 ):
        OpenAI.api_key = os.environ["OPENAI_API_KEY"]
        
        self.client = OpenAI()
        self.model = model
        self.system_prompt = system_prompt
        self.messages = []
        self.messages.append({"role":"system", "content":system_prompt})
        self.input_tokens = 0
        self.output_tokens = 0
        self.counter = 0
        self.raw_messages = []
        
        self.logger = setup_logger(log_level)
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"System Prompt: {self.system_prompt}")
        
    def _extract_content(self, response):
        return response.choices[0].message.content
    
    def _apply_request(self, messages: list, temporary: bool):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        self.logger.debug(f"Raw Output: {response}")
        assistant_message = self._extract_content(response) 
        self.logger.info(f"Responsed_message: {assistant_message}") 
        
        if not temporary:
            
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            self.logger.debug(f"Input_tokens: {input_tokens}")
            self.logger.debug(f"Output_tokens: {output_tokens}")
            self.logger.debug(f"Total_tokens: {total_tokens}")
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens  
            
            self.raw_messages.append(
                {
                    "id": self.counter,
                    "request": deepcopy(messages),
                    "response": response.model_dump()
                }
            )
            self.counter += 1

        return assistant_message  
                
    def send_soft_temporary_message(self, user_message: str) -> str:
        messages = deepcopy(self.messages)
        messages.append({"role":"user", "content":user_message})
        assistant_message = self._apply_request(messages, temporary=True)

        return assistant_message
    
    def send_hard_temporary_message(self, user_message: str) -> str:
        messages = []
        messages.append({"role":"system", "content":self.system_prompt})
        messages.append({"role":"user", "content":user_message})
        assistant_message = self._apply_request(messages, temporary=True)
        
        return assistant_message
    
    def send_message(self, user_message: str) -> str:
        self.messages.append({"role":"user", "content":user_message})
        assistant_message = self._apply_request(self.messages, temporary=False)
        self.messages.append({"role":"assistant", "content":assistant_message})
        
        return assistant_message
    
    def export_history(self):
        return self.messages
    
    def expoert_raw_history(self):
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
    python -m module.llm.gpt --log_level INFO
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set logging level for GPTClient")
    args = parser.parse_args()
    
    system_prompt = "당신은 인공지능을 가르치는 교수님입니다."
    gpt = GPTClient(system_prompt=system_prompt, log_level=args.log_level)

    question = "attention에 대해 설명해주세요."
    print(f"질문 1: {question}")
    res = gpt.send_message(question)
    print("GPT 응답 1:\n", res, "\n")
    print(gpt.get_tokens())

    question =  "cnn에 대해 설명해주세요."
    print(f"질문 2: {question}")
    res = gpt.send_message(question)
    print("GPT 응답 2:\n", res, "\n")
    print(gpt.get_tokens())

    question = "지금까지 배운 것에 대해 설명해주세요."
    print(f"질문 3: {question}")
    res = gpt.send_message(question)
    print("GPT 응답 3:\n", res, "\n")
    print(gpt.get_tokens())

    question = "아까 물은 cnn과 방송국으로서의 cnn은 무슨 차이에요?"
    print(f"Soft temporary 질문 1: {question}")
    soft_temp = gpt.send_soft_temporary_message(question)
    print("GPT 응답 (soft temporary):\n", soft_temp, "\n")
    print(gpt.get_tokens())
    
    question = "지금까지 대화에 대하여 요약해줘"
    print(f"Soft temporary 질문 2: {question}")
    soft_temp = gpt.send_soft_temporary_message(question)
    print("GPT 응답 (soft temporary):\n", soft_temp, "\n")
    print(gpt.get_tokens())
    
    question = "아까 물은 cnn과 방송국으로서의 cnn은 무슨 차이에요?"
    print(f"Hard temporary 질문 1: {question}")
    hard_temp = gpt.send_hard_temporary_message(question)
    print("GPT 응답 (hard temporary):\n", hard_temp, "\n")
    print(gpt.get_tokens())
    
    question = "알파고는 어떻게 바둑을 이겼나요?"
    print(f"Hard temporary 질문 1: {question}")
    hard_temp = gpt.send_hard_temporary_message(question)
    print("GPT 응답 (hard temporary):\n", hard_temp, "\n")
    print(gpt.get_tokens())
    
    question = "지금까지 대화에 대하여 요약해줘"
    print(f"Hard temporary 질문 3: {question}")
    hard_temp = gpt.send_hard_temporary_message(question)
    print("GPT 응답 (hard temporary):\n", hard_temp, "\n")
    print(gpt.get_tokens())
    
    print("전체 대화 기록 (export_history):")
    for msg in gpt.export_history():
        print(f"[{msg['role'].upper()}] {msg['content']}\n")
