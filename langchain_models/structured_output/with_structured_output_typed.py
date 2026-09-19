from langchain_openai import  ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict ,Annotated,Optional

load_dotenv()

model = ChatOpenAI()

#schema
class Review(TypedDict):
    summary:Annotated[str,"A brief summaru of the review"]
    sentiment:Annotated[str,"Return sentiment of the review rank 1 to 5 with string "]
    pros: Annotated[Optional[list[str]],"Write down all pros inside the list"]
    cons: Annotated[Optional[list[str]],"Write down all cons inside the list"]

structured_model = model.with_structured_output(Review)

result  = structured_model.invoke("""The hardwarte is grteate . but hte softeware feels bloated . There are  too many pre-installed app that  I can't imporve also the Ui is looks putdated comapre to  other bradnd. Hping for a softare update to fix this""")
print(result)
print(result['summary'])
print(result['sentiment'])
