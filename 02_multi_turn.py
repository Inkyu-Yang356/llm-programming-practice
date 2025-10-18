from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

client = OpenAI(api_key=api_key)

def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.9
    )
    return response.choices[0].message.content

def turn(turn_type="single"):
    conversation_history = [] # 멀티턴 대화 내용을 저장하기 위한 리스트 초기화

    while True:
        user_input = input("User: ")
        
        if user_input.lower() == "exit":
            print("Exiting the chat.")
            break

        if turn_type == "single":
            messages = [
                {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},
                {"role": "user", "content": user_input}
            ]
        elif turn_type == "multi":

            if not conversation_history:
                conversation_history.append({"role": "system", "content": "너는 사용자를 도와주는 상담사야."})
            conversation_history.append({"role": "user", "content": user_input})
            messages = conversation_history

        # 모델에 질의응답
        assistant_response = get_response(messages)

        # 모델 응답 출력
        print("Assistant:", assistant_response)

        if turn_type == "multi":
            # GPT 응답을 다음 대화 내용 전달을 위해 conversation history에 추가
            conversation_history.append({"role": "assistant", "content": assistant_response})

# Example usage
print("Choose mode: 'single' or 'multi' ")
mode = input("Enter mode: ").strip().lower()
if mode in ["single", "multi"]:
    turn(turn_type=mode)
else:
    print("Invalid mode. Please restart and choose 'single' or 'multi'.")