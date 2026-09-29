
import os
import operator
from typing import TypedDict, Annotated

import psycopg
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


load_dotenv()


# --------------------------------------------------
# Environment
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


# --------------------------------------------------
# LLM
# --------------------------------------------------

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0,
# )
llm = ChatOpenAI()

# --------------------------------------------------
# State
# --------------------------------------------------

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# --------------------------------------------------
# Flight Agent
# --------------------------------------------------

def flight_agent(state: TravelState):
    query = state["user_query"]

    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Hotel Agent
# --------------------------------------------------

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"

    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Itinerary Agent
# --------------------------------------------------

def itinerary_agent(state: TravelState):

    prompt = f"""
Create a travel itinerary based on the following information.

User Query:
{state["user_query"]}

Flight Results:
{state["flight_results"]}

Hotel Results:
{state["hotel_results"]}

Create a practical itinerary including:
- Travel dates
- Destination
- Flight information
- Hotel information
- Daily activities
- Important notes
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="You are an expert travel planner."
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Final Response Agent
# --------------------------------------------------

def final_agent(state: TravelState):

    final_prompt = f"""
Generate a clear final travel response for the user.

User Request:
{state["user_query"]}

Flights:
{state["flight_results"]}

Hotels:
{state["hotel_results"]}

Itinerary:
{state["itinerary"]}

Present the answer clearly with sections for:
1. Flights
2. Hotels
3. Itinerary
4. Important notes
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="You are a helpful travel booking assistant."
            ),
            HumanMessage(content=final_prompt),
        ]
    )

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# --------------------------------------------------
# Build Graph
# --------------------------------------------------

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# --------------------------------------------------
# PostgreSQL Checkpointer
# --------------------------------------------------

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()


# --------------------------------------------------
# Compile Application
# --------------------------------------------------

app = graph.compile(
    checkpointer=checkpointer
)


# --------------------------------------------------
# CLI
# --------------------------------------------------

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "user_everest"
        }
    }

    user_input = input(
        "Enter travel request: "
    )

    initial_state = {
        "messages": [
            HumanMessage(content=user_input)
        ],
        "user_query": user_input,
        "flight_results": "",
        "hotel_results": "",
        "itinerary": "",
        "llm_calls": 0,
    }

    result = app.invoke(
        initial_state,
        config=config,
    )

    print("\n")
    print("=" * 60)
    print("FINAL RESPONSE")
    print("=" * 60)

    # Last AI message is the final response
    for message in reversed(result["messages"]):

        if isinstance(message, AIMessage):
            print("\n")
            print(message.content)
            break

    print("\n")
    print("=" * 60)
    print(
        f"LLM calls: {result['llm_calls']}"
    )
