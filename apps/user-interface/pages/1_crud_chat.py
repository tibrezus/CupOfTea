import uuid
import os
import asyncio
import streamlit as st
from ollama import AsyncClient, ResponseError
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem

st.title("Chat with Ollama")

# Initialize the Ollama client
ollamaClient = AsyncClient(host='http://ollama.zuru.local:11434')

# Dapr env variables
stateStore = os.getenv('DAPR_STATE_STORE', 'statestore')

def saveMessages(messages):
    """Save chat messages to the Dapr state store."""
    with DaprClient() as daprClient:
        state = StateItem(key="crud_chat", value=str(messages))
        daprClient.save_state(stateStore, key=state.key, value=state.value)

def loadMessages():
    """Load chat messages from the Dapr state store."""
    with DaprClient() as daprClient:
        resp = daprClient.get_state(stateStore, "crud_chat")
        if resp and resp.data:
            storedData = resp.data
            try:
                return eval(storedData.decode('utf-8'))
            except SyntaxError:
                print("Failed to decode stored data.")
                return []
        return []

# Initialize session state for model selection and message history
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = "llama3"

if "messages" not in st.session_state:
    st.session_state.messages = loadMessages()

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        buttonKey = f"Delete message {message['id']}"
        if st.button("Delete message", key=buttonKey):
            # Remove the message from the local state
            st.session_state.messages.pop(i)
            # Save the updated state back to Dapr
            saveMessages(st.session_state.messages)
            # Refresh the UI
            st.rerun()

async def chat(prompt):
    model = st.session_state["ollama_model"]
    chatMessage = {"role": "user", "content": prompt}
    # Include all messages in st.session_state.messages as context
    context = st.session_state.messages + [chatMessage]
    try:
        chatResponse = await ollamaClient.chat(
            model=model,
            messages=context
        )
    except ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            await ollamaClient.pull(model)
        return None
    return chatResponse['message']['content']

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt, "id": str(uuid.uuid4())})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = asyncio.run(chat(prompt))
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response, "id": str(uuid.uuid4())})
    saveMessages(st.session_state.messages)
    # Refresh the UI
    st.rerun()