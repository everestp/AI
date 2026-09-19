from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser ,StrOutputParser

load_dotenv()

prompt1 = PromptTemplate(
  template="Generate a detail report on  {topic}",
  input_variables=['topic']
 )
prompt2 = PromptTemplate(
  template="Generate a  5 poiner summary from the follwing \n  {topic}",
  input_variables=['text']
 )

model = ChatOpenAI()
parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser
result = chain.invoke({'topic':'monero'})
print(result)
