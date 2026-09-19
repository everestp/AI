from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

em = OpenAIEmbeddings(model="text-embedding-3-large",dimensions=32)
result = em.embed_query("delhi")
print(result)
