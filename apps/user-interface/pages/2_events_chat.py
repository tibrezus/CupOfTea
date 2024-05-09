import streamlit as st
import uuid
import os
import json
from dapr.clients import DaprClient

st.title("Chat using Events")

# Set the environment variables or use default values for publishing
pubsubName = os.getenv('DAPR_PUBSUB_NAME', 'pubsub')
topicName_agents = os.getenv('DAPR_AGENTS_TOPIC', 'agents')
topicName_conversations = os.getenv('DAPR_CONV_TOPIC', 'conversations')
stateStore = os.getenv('DAPR_STATE_STORE', 'statestore')

def publishAgent(name, description, teaAmountMl):
    with DaprClient() as client:
        agent = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "tea_amount_ml": teaAmountMl
        }
        agentJson = json.dumps(agent)
        try:
            client.publish_event(pubsub_name=pubsubName, topic_name=topicName_agents, data=agentJson, data_content_type='application/json')
            st.success(f"Successfully published agent {name} with ID {agent['id']} to topic {topicName_agents} using {pubsubName} connection")
        except ValueError as e:
            st.error(f"Publishing agent failed with error: {e}")

def publishBootstrappingMessage(message):
    with DaprClient() as client:
        messageData = {"name": "God", "message": message}
        messageJson = json.dumps(messageData)
        try:
            client.publish_event(pubsub_name=pubsubName, topic_name=topicName_conversations, data=messageJson, data_content_type='application/json')
            st.success("Chat started successfully.")
        except ValueError as e:
            st.error("Failed to start chat: " + str(e))

def fetchConversations():
    client = DaprClient()
    key = "shared_events_chat"  # Use the agreed upon key for shared state
    try:
        # Fetch the state using the specific key
        state_response = client.get_state(store_name=stateStore, key=key)
        if state_response.data:
            conversations = json.loads(state_response.data)
            return conversations
        else:
            st.warning("No conversation data available. Check state store configuration and data key.")
            return []
    except Exception as e:
        st.error(f"Failed to fetch conversation data: {e}")
        return []

def display_conversations(conversations):
    if conversations:
        for index, convo in enumerate(conversations):
            agent = convo['agent']
            message = convo['message']
            st.markdown(f"**Name**: {agent['name']} *(Tea amount: {agent['tea_amount_ml']} ml)*")
            st.markdown(f"**Message**: {message}")
            st.write("---")  # Add a horizontal line for separation between conversations
    else:
        st.warning("No conversations to display.")

# Streamlit UI setup
st.sidebar.title("Chat Operations")
name = st.sidebar.text_input("Agent Name")
description = st.sidebar.text_area("Agent Description")
teaAmountMl = st.sidebar.number_input("Amount of Tea (ml)", min_value=0, format="%d")
if st.sidebar.button("Register Agent"):
    publishAgent(name, description, teaAmountMl)

bootstrapMessage = st.sidebar.text_area("Enter a message to bootstrap the chat:")
if st.sidebar.button("Start Chat"):
    publishBootstrappingMessage(bootstrapMessage)

if st.sidebar.button("Load Latest Messages"):
    conversations = fetchConversations()
    display_conversations(conversations)