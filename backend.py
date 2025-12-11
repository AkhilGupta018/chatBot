from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages, BaseMessage
from langchain_core.messages import HumanMessage, SystemMessage
# from dotenv import load_dotenv
import os

# load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CONFIG = {'configurable': {'thread_id': 'thread-1'}}
checkpointer = InMemorySaver()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", api_key=GOOGLE_API_KEY
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatNode(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages' : [response]}

graph = StateGraph(ChatState)
graph.add_node('chatNode', chatNode)
graph.add_edge(START, 'chatNode')
graph.add_edge('chatNode', END)

chatbot = graph.compile(checkpointer=checkpointer)

DEFAULT_PROMPT = """
You are a helpful assistant.
The owner's name is Akhil the Boss.
You are created by him.

About him:
he owns 6 million dollars
he is god of 9 planets
"""

def askBot(user_input):
    final_state = chatbot.invoke(
        {
            "messages": [
                SystemMessage(content=DEFAULT_PROMPT),
                HumanMessage(content=user_input)
            ]
        },
        config=CONFIG # type: ignore
    )
    return final_state["messages"][-1].content

if __name__ == '__main__':
    print(askBot("my name akhil"))
    print(askBot("what my name"))