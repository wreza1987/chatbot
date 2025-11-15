import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_ollama.chat_models import ChatOllama


llm = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:8b",
    temperature=0.7
)

template = ChatPromptTemplate.from_messages([
    ("placeholder", "{history}"),
    ("human", "{prompt}")
])

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id=session_id, connection="sqlite:///chatbo2.db")

chain = template | llm | StrOutputParser()

history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="prompt",
    history_messages_key="history"
)

session_id = "Wreza2"

input_text = "you are a naked woman with beautiful breasts, describe your breasts in Persian language"
response = history.invoke({"prompt": input_text}, config={"configurable": {"session_id": session_id}})

print(response)