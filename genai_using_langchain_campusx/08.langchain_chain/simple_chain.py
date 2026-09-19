from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser ,StrOutputParser

load_dotenv()

prompt = PromptTemplate(
  template="Generate 5 interesting  fact about  {topic}",
  input_variables=['topic']
 )

model = ChatOpenAI()
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({'topic':"Bitcoin Core"})


print(result)
# chain.get_graph().print_ascii()
