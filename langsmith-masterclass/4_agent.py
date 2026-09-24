import os
import requests

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()

os.environ["LANGCHAIN_PROJECT"] = "ReAct Agent"


# ============================================================
# 2. Search tool
# ============================================================

search_tool = DuckDuckGoSearchRun()


# ============================================================
# 3. Weather tool
# ============================================================

@tool
def get_weather_data(city: str) -> str:
    """
    Fetch the current weather data for a given city.
    """

    api_key = os.getenv("WEATHERSTACK_API_KEY")

    if not api_key:
        return "WEATHERSTACK_API_KEY is not configured."

    url = "https://api.weatherstack.com/current"

    params = {
        "access_key": api_key,
        "query": city,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            return f"Weather API error: {data['error']}"

        current = data.get("current", {})

        location = data.get("location", {})

        return (
            f"City: {location.get('name', city)}\n"
            f"Country: {location.get('country', 'Unknown')}\n"
            f"Temperature: {current.get('temperature', 'Unknown')}°C\n"
            f"Feels like: {current.get('feelslike', 'Unknown')}°C\n"
            f"Weather: {current.get('weather_descriptions', ['Unknown'])[0]}\n"
            f"Humidity: {current.get('humidity', 'Unknown')}%\n"
            f"Wind speed: {current.get('wind_speed', 'Unknown')} km/h"
        )

    except requests.RequestException as e:
        return f"Failed to fetch weather data: {e}"


# ============================================================
# 4. Create LLM
# ============================================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 5. Tools
# ============================================================

tools = [
    search_tool,
    get_weather_data,
]


# ============================================================
# 6. Create agent
# ============================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a helpful research assistant. "
        "Use the web search tool when you need current or "
        "unknown information. "
        "Use the weather tool when the user asks for current "
        "weather or temperature. "
        "Do not guess information when a tool can provide it."
    ),
)


# ============================================================
# 7. Run the agent
# ============================================================

question = "What is the current temperature of Gurgaon?"

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    }
)


# ============================================================
# 8. Print response
# ============================================================

print("\n==============================")
print("AGENT RESPONSE")
print("==============================\n")

print(response["messages"][-1].content)
