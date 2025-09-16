from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Make sure to replace "your_api_key_here" with your actual OpenAI API key.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

response = client.chat.completions.create(
#    model="gpt-3.5-turbo",
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},  # System Prompt
        {"role": "user", "content": "2022년 월드컵 우승 팀은 어디야?"}  # User Prompt
    ]
)

# Print the entire response object
print(response)

# Print just the content of the first message in the choices
print(response.choices[0].message.content)

# ChatCompletion(id='chatcmpl-CGGGK6Ot2L5UNFJbfNxwOhA3mJe06', 
# choices=[Choice(finish_reason='stop', index=0, logprobs=None, 
# message=ChatCompletionMessage(content='2022년 FIFA 월드컵 우승 팀은 아르헨티나입니다. 
# 아르헨티나는 결승전에서 프랑스를 상대로 승리를 거두어 우승을 차지했습니다.', refusal=None, 
# role='assistant', audio=None, function_call=None, tool_calls=None, annotations=[]))], 
# created=1757991796, model='gpt-4o-2024-08-06', object='chat.completion', 
# service_tier='default', system_fingerprint='fp_f33640a400', 
# usage=CompletionUsage(completion_tokens=46, prompt_tokens=30, total_tokens=76, 
# completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, 
# audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), 
# prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))

# 2022년 FIFA 월드컵 우승 팀은 아르헨티나입니다. 
# 아르헨티나는 결승전에서 프랑스를 상대로 승리를 거두어 우승을 차지했습니다.
