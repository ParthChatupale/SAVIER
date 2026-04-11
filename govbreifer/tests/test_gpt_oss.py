from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()



client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("GOVBREIFER_NIM_API_KEY_FINAL")
)

completion = client.chat.completions.create(
  model="openai/gpt-oss-120b",
  messages=[{"role":"user","content":"Hello how are you?"}],
  temperature=1,
  top_p=1,
  max_tokens=4096,
  stream=True
)

for chunk in completion:
  if not getattr(chunk, "choices", None):
    continue
  reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
  if reasoning:
    print(reasoning, end="")
  if chunk.choices and chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")



client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("GOVBREIFER_NIM_API_KEY_FAST")
)

completion = client.chat.completions.create(
  model="openai/gpt-oss-20b",
  messages=[{"role":"user","content":"hantush kaisa hai ?"}],
  temperature=1,
  top_p=1,
  max_tokens=4096,
  stream=True
)

for chunk in completion:
  if not getattr(chunk, "choices", None):
    continue
  reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
  if reasoning:
    print(reasoning, end="")
  if chunk.choices and chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")

