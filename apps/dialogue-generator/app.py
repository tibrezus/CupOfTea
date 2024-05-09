import json
import logging
import os

import uvicorn
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem
from fastapi import FastAPI
from langchain_community.llms import Ollama
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Set environment variables
llmName = os.getenv("OLLAMA_LLM_NAME", "llama3")
llmUrl = os.getenv("OLLAMA_LLM_URL", "http://ollama.zuru.local:11434")

# Initialize the Ollama model
llm = Ollama(model=llmName, base_url=llmUrl)

# Dapr Pub/Sub names
pubsubName = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
agentsTopic = os.getenv("DAPR_AGENTS_TOPIC", "agents")
conversationsTopic = os.getenv("DAPR_CONVERSATIONS_TOPIC", "conversations")

# State store name
stateStore = os.getenv("DAPR_STATE_STORE", "statestore")


class Agent(BaseModel):
    id: str
    name: str
    description: str
    tea_amount_ml: int

class DialogueRequest(BaseModel):
    agent: Agent
    message: str


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    # Return an empty list as this app doesn't subscribe to any topics
    return []

@app.get("/dapr/config")
async def dapr_config():
    # Return an empty dictionary as this app doesn't provide any specific configuration for the Dapr sidecar
    return {}

def loadState():
    client = DaprClient()
    key = "shared_events_chat"
    try:
        # Retrieve the current state
        resp = client.get_state(store_name=stateStore, key=key)
        if resp and resp.data:
            # Decode and parse the stored data
            storedData = json.loads(resp.data.decode("utf-8"))
            return storedData
        else:
            # If there's no current state, return an empty list
            return []
    except Exception as e:
        logging.error(f"Failed to load state: {e}")
        return []

@app.post("/generate")
async def invokeDialogueGenerator(request: DialogueRequest):
    data = request.dict()

    agent = data.get("agent")
    message = data.get("message")

    senderName = agent.get("name")
    description = agent.get("description")

    storedData = loadState()
    lastMessages = storedData[-12:]  

    lastMessagesStr = "\n".join([msg["message"] for msg in lastMessages])

    prompt = f"""Character Description: {description}

    Latest Messages: {lastMessagesStr}

    Context: The conversation is light-hearted and humorous, unfolding over a cup of tea. It's brief but engaging, offering a glimpse into the character's quirky personality.

    Response:"""

    # ... (rest of the code)

    tokenCount = 0
    responseChunks = []
    for chunk in llm.stream(prompt):
        responseChunks.append(chunk)
        tokenCount += len(chunk.split())  # Count the words in each chunk

    generatedResponse = "".join(responseChunks).strip()

    # Adjust tea_amount_ml based on token count
    teaAmountMlAdjusted = agent["tea_amount_ml"] - int(tokenCount / 100)
    agent["tea_amount_ml"] = max(
        teaAmountMlAdjusted, 0
    )  # Ensure it doesn't go negative

    # Prepare data for publishing
    agentData = agent
    messageData = {"message": generatedResponse, "name": senderName}

    # Publish updated agent info
    logging.info(f"Publishing updated agent info to {agentsTopic}")
    publishToDapr(pubsubName, agentsTopic, json.dumps(agentData))
    # Publish generated message
    logging.info(f"Publishing generated message to {conversationsTopic}")
    publishToDapr(pubsubName, conversationsTopic, json.dumps(messageData))

    logging.info("Saving agent data to state store")
    saveToState(data)

    return {"content_type": "text/plain", "data": generatedResponse}


def publishToDapr(pubsub, topicName, data):
    client = DaprClient()
    logging.info(f"Publishing data to {topicName} in {pubsub}")
    client.publish_event(
        pubsub_name=pubsub,
        topic_name=topicName,
        data=data,
        data_content_type="application/json",
    )

def saveToState(data):
    client = DaprClient()
    key = "shared_events_chat"
    try:
        # Retrieve the current state
        resp = client.get_state(store_name=stateStore, key=key)
        if resp and resp.data:
            # Decode and parse the stored data
            storedData = json.loads(resp.data.decode("utf-8"))
        else:
            # If there's no current state, start a new list of messages
            storedData = []

        # Append the new message to the list of messages
        storedData.append(data)

        # Convert the updated list of messages to a byte string
        data_bytes = json.dumps(storedData).encode("utf-8")
        # Save the updated state
        client.save_state(store_name=stateStore, key=key, value=data_bytes)
        logging.info(f"Saved updated conversations to state store under key {key}")
    except Exception as e:
        logging.error(f"Failed to save state: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5400)
