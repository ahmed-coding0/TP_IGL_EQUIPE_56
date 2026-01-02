from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict
class SimpleState(TypedDict):
    count: int

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key="AIzaSyALs603DgvRL66G5owL6D3HP3q7M8Cy73g")


def ask_gemini(state):
    prompt = f"What is {state['count']} + 10?"
    response = llm.invoke(prompt)
    print(f"Gemini says: {response.content}")
    return state

workflow = StateGraph(SimpleState)
workflow.add_node("ask", ask_gemini)
workflow.set_entry_point("ask")
workflow.add_edge("ask", END)

app = workflow.compile()
app.invoke({"count": 5})