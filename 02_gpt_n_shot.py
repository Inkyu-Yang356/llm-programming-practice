from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

client = OpenAI(api_key = api_key)

model = "gpt-4o"
zero_shot_msg = [
    {"role": "system", "content": "너는 유치원생이야. 유치원생처럼 답변해줘."},  # System Prompt
    {"role": "user", "content": "오리"}  # User Prompt
]

one_shot_msg = [
    {"role": "system", "content": "너는 유치원생이야. 유치원생처럼 답변해줘."},  # System Prompt
    {"role": "user", "content": "참새"},  # User Prompt
    {"role": "assistant", "content": "짹짹"},  # Assistant Response (pattern training)
    {"role": "user", "content": "오리"}  # User Prompt
]

few_shot_msg = [
    {"role": "system", "content": "너는 유치원생이야. 유치원생처럼 답변해줘."},  # System Prompt
    {"role": "user", "content": "참새"},  # User Prompt
    {"role": "assistant", "content": "짹짹"},  # Assistant Response (pattern training)
    {"role": "user", "content": "말"},  # User Prompt
    {"role": "assistant", "content": "히이잉"},  # Assistant Response (pattern training)
    {"role": "user", "content": "개구리"},  # User Prompt
    {"role": "assistant", "content": "개굴개굴"},  # Assistant Response (pattern training)
    {"role": "user", "content": "오리"}  # User Prompt
]

# Zero-shot, One-shot, Few-shot examples
zero_response = client.chat.completions.create(
    model=model,
    messages= zero_shot_msg,  
    temperature=0.9,  # Adjust temperature for creativity
)

one_response = client.chat.completions.create(
    model=model,
    messages= one_shot_msg,  
    temperature=0.9,  # Adjust temperature for creativity
)

few_response = client.chat.completions.create(
    model=model,
    messages= few_shot_msg,  
    temperature=0.9,  # Adjust temperature for creativity
)

print("Zero-shot response:", zero_response.choices[0].message.content)  # Zero-shot response: 꽥꽥! 오리는 물에서 헤엄치고 꽥꽥 소리 내는 귀여운 동물이야! 너도 오리 본 적 있어? 물에서 둥둥 떠다니 는 모습이 정말 재미있어!
print("One-shot response:", one_response.choices[0].message.content)  # One-shot response: 꽥꽥! 오리는 물에서 헤엄도 잘 치고 땅에서도 걸어다녀! 귀엽지?
print("Few-shot response:", few_response.choices[0].message.content)  # Few-shot response: 꽥꽥