
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder


#chat template
chat_template = ChatPromptTemplate([
    ('system',"You are a helpful customer support agent "),
    MessagesPlaceholder(variable_name="chat_history"),
      ('human',"{query}")
    # SystemMessage(content ="You are a helpful {domain} expert "),
    # HumanMessage(content="Explain in simple term , What is {topic}")
])
chat_history=[]
#load the chat histroy
with open('chat_history.txt') as f:
   chat_history.append(f.readlines())

print(chat_history)


# create prompt
chat_template.invoke({'chat_history':chat_history ,'query':"Where i is my refund"})
