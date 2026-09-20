import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --------------------------------------------------
# Imports
# --------------------------------------------------

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_community.vectorstores import FAISS

from langchain_core.prompts import PromptTemplate

from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)

from langchain_core.output_parsers import StrOutputParser


# ==================================================
# STEP 1: INDEXING
# ==================================================

# --------------------------------------------------
# Step 1a: Document Ingestion
# --------------------------------------------------

video_id = "H9c9A2rNrFA"

try:
    # Create YouTube Transcript API client
    api = YouTubeTranscriptApi()

    # Fetch transcript
    transcript_list = api.fetch(
        video_id,
        languages=["en"]
    )

    # Convert transcript snippets into plain text
    transcript = " ".join(
        snippet.text for snippet in transcript_list
    )

    print("Transcript fetched successfully!")
    print()
    print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")
    transcript = ""

except Exception as e:
    print(f"Error fetching transcript: {e}")
    transcript = ""


# --------------------------------------------------
# Step 1b: Text Splitting
# --------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.create_documents([transcript])

print()
print("Number of chunks:", len(chunks))


# --------------------------------------------------
# Step 1c & 1d:
# Embedding Generation + Vector Store
# --------------------------------------------------

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

print("Vector store created successfully!")


# ==================================================
# STEP 2: RETRIEVAL
# ==================================================

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4
    }
)

# Test retrieval
retrieved_docs = retriever.invoke(
    "What is DeepMind?"
)

print()
print("Retrieved documents:")
for doc in retrieved_docs:
    print(doc.page_content)
    print("------------------------")


# ==================================================
# STEP 3: AUGMENTATION
# ==================================================

# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)


# --------------------------------------------------
# Prompt
# --------------------------------------------------

prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Answer ONLY from the provided transcript context.

If the context is insufficient, just say:
"I don't know based on the provided transcript."

Context:
{context}

Question:
{question}
""",
    input_variables=[
        "context",
        "question"
    ]
)


# --------------------------------------------------
# Test a question
# --------------------------------------------------

question = """
Is the topic of nuclear fusion discussed in this video?
If yes, what was discussed?
"""

retrieved_docs = retriever.invoke(question)

context_text = "\n\n".join(
    doc.page_content
    for doc in retrieved_docs
)

print()
print("Retrieved Context:")
print(context_text)


# ==================================================
# STEP 4: GENERATION
# ==================================================

final_prompt = prompt.invoke({
    "context": context_text,
    "question": question
})

answer = llm.invoke(final_prompt)

print()
print("Answer:")
print(answer.content)


# ==================================================
# BUILDING THE RAG CHAIN
# ==================================================

# --------------------------------------------------
# Format retrieved documents
# --------------------------------------------------

def format_docs(retrieved_docs):
    return "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )


# --------------------------------------------------
# Parallel Chain
# --------------------------------------------------

parallel_chain = RunnableParallel({
    "context": retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})


# Test parallel chain
result = parallel_chain.invoke(
    "What is  bitcoin ?"
)

print()
print("Parallel Chain Result:")
print(result)


# --------------------------------------------------
# Output Parser
# --------------------------------------------------

parser = StrOutputParser()


# --------------------------------------------------
# Main RAG Chain
# --------------------------------------------------

main_chain = (
    parallel_chain
    | prompt
    | llm
    | parser
)


# ==================================================
# FINAL QUESTION
# ==================================================

answer = main_chain.invoke(
    "Can you summarize the video?"
)

print()
print("Final Answer:")
print(answer)
