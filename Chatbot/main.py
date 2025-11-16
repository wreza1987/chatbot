import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_ollama.chat_models import ChatOllama


llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1:8b",
    temperature=0.7
)

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id=session_id, connection="sqlite:///chatbot.db")


session_id = ""

st.title("HI THERE!")
st.write("You can ask me")

with st.sidebar:
    session_id = st.text_input("Enter your name", session_id)
    role = st.radio("Level: ", ["Beginner", "Mid", "Expert", "PHD"])

    if st.button("Start new chat"):
        st.session_state.chat_history = []
        get_session_history(session_id).clear()


st.markdown(
    """
    <div style='display: flex; height: 70vh; justify-content: center; align-items: center;'>
        <h2>What can I help you today?</h2>
    </div>
    """,
    unsafe_allow_html=True
)



if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

template = ChatPromptTemplate.from_messages([
    ("placeholder", "{history}"),
    ("system", f"You are a {role}-level user to answer this query, and just and just answer in Persian language!"),
    ("human", "{prompt}")
])



chain = template | llm | StrOutputParser()


def stream_history(chain, session_id, prompt):
    history = RunnableWithMessageHistory(
        chain,
        get_session_history=get_session_history,
        input_messages_key="prompt",
        history_messages_key="history"
    )

    for resp in history.stream({"prompt": prompt}, config={"configurable": {"session_id": session_id}}):
        yield resp 


prompt = st.chat_input("Ask Me!")
if prompt:
    response = stream_history(chain, session_id, prompt)
    st.session_state.chat_history.append({'role': 'user', 'content': prompt})

    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        stream_response = st.write_stream(response)

    st.session_state.chat_history.append({'role': 'assistant', 'content': stream_response})
    
