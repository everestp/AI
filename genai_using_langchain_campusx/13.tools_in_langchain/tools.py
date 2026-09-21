from langchain_openai import ChatOpenAI
from  langchain_core.tools import tool

import requests
from dotenv import load_dotenv
load_dotenv()

#tool create
@tool
def multiply(a:int , b :int)->int:
    """Giben 2 number a and b this tool return  product"""
    return a * b

#tool binding
llm = ChatOpenAI()
llm_with_tool = llm.bind_tools([multiply])

result = llm_with_tool.invoke('can you multily 16 with 6')

print(result)
