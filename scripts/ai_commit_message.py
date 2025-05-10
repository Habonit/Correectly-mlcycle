import sys
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

template_path = "scripts/commit_template.txt"

load_dotenv()

api_key = os.getenv("COMMIT_OPENAI_API_KEY")
model = os.getenv("COMMIT_MODEL", "gpt-4o")

if not api_key:
    print("❌ OPENAI_API_KEY가 설정되어 있지 않습니다.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

diff = sys.argv[1]

with open(template_path, "r") as f:
    prompt_template = f.read()

prompt = prompt_template.format(diff=diff)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(response.choices[0].message.content)