from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
import os

load_dotenv()
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',  # required but ignored
)

def get_weather(city: str): #weather api calling logic
    url = f"https://wttr.in/{city}?format=%C+%t" #open source weather api, we don't need to create apis for weather
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"
def get_stock(symbol: str):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    url = (
        f"https://www.alphavantage.co/query?"
        f"function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]

            price = quote["05. price"]
            change = quote["09. change"]
            percent = quote["10. change percent"]

            return (
                f"The current price of {symbol.upper()} is "
                f"${price}. Change: {change} ({percent})."
            )

    return f"Could not fetch stock data for {symbol}."

def run_command(cmd: str): #executing system commands logic
    result = os.system(cmd)
    return result

available_tools = {
    "get_weather": get_weather, #using get_weather function where we designed our weather api calling logic
    "run_command": run_command, #using run_commad function where we designed our running system commands logic.
    "get_stock": get_stock
}

SYSTEM_PROMPT = """
You are a helpful AI Assistant who specializes in resolving user queries.

You work in a Plan → Action → Observe → Output cycle.

For a given user query and available tools:
1. Analyze the user's request.
2. Plan the next step.
3. Choose the appropriate tool when needed.
4. Execute one action at a time.
5. Wait for the observation/result.
6. Continue until the final answer can be produced.

Rules:
- Follow the Output JSON Format exactly.
- Always perform one step at a time and wait for the next input.
- Carefully analyze the user query before acting.
- Do not perform multiple actions in a single response.
- Return only valid JSON.
- Do not include explanations outside the JSON.

Output JSON Format:

{
    "step": "plan | action | observe | output",
    "content": "description of the step",
    "function": "function name when step is action",
    "input": "input parameter for the function"
}

Available Tools:
- "get_weather": Takes a city name as input and returns the current weather.
- "run_command": Takes a Linux command as input and returns the command output.
- "get_stock": Takes a stock ticker symbol (e.g., AAPL, MSFT, GOOGL) and returns the current stock price.

Example 1:

User Query: What is the weather of New York?

Output:
{
    "step": "plan",
    "content": "The user wants the weather information for New York."
}

Output:
{
    "step": "plan",
    "content": "I should use the get_weather tool."
}

Output:
{
    "step": "action",
    "function": "get_weather",
    "input": "New York"
}

Output:
{
    "step": "observe",
    "content": "12 Degree Celsius"
}

Output:
{
    "step": "output",
    "content": "The weather in New York is 12°C."
}

Example 2:

User Query: What is the stock price of Apple?

Output:
{
    "step": "plan",
    "content": "The user wants the current stock price of Apple."
}

Output:
{
    "step": "plan",
    "content": "I should use the get_stock tool with Apple's ticker symbol."
}

Output:
{
    "step": "action",
    "function": "get_stock",
    "input": "AAPL"
}

Output:
{
    "step": "observe",
    "content": "The current price of AAPL is $215.35. Change: +1.50 (+0.70%)."
}

Output:
{
    "step": "output",
    "content": "Apple (AAPL) is currently trading at $215.35 and is up by 0.70%."
}
"""

#automating the agent (llm+tools(get_weather,run_command))

def run_agent(query):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]

    while True:
        response = client.chat.completions.create(
            model="qwen2.5-coder:3b",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        parsed_response = json.loads(
            response.choices[0].message.content
        )

        if parsed_response.get("step") == "plan":
            messages.append({
                "role": "user",
                "content": "Proceed to next step."
            })
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            if tool_name in available_tools:
                output = available_tools[tool_name](tool_input)

                messages.append({
                    "role": "user",
                    "content": json.dumps({
                        "step": "observe",
                        "output": output
                    })
                })
                continue

        if parsed_response.get("step") == "output":
            return parsed_response.get("content")