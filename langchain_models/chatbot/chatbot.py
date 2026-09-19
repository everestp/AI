from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()
chat_hisotry = [
     SystemMessage(content="You are a expert Bitcoin core Developer")
]
model = ChatOpenAI(model="gpt-4", temperature= 0 , max_completion_tokens=50)

while True:
     user_input=input("You:")
     chat_hisotry.append(HumanMessage(content=user_input))
     if user_input=="exit":
          break
     result=model.invoke(chat_hisotry)
     chat_hisotry.append(result.content)
     print("AI: ",AIMessage(result.content))
     print(chat_hisotry)
