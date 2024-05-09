import json
import logging
import os
import random

from cloudevents.sdk.event import v1
from dapr.clients import DaprClient
from dapr.ext.grpc import App

# Setup logging
logging.basicConfig(level=logging.INFO)

# Constants for Dapr configuration
stateStore = os.getenv("DAPR_STATE_STORE", "statestore")
pubsubName = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
agentsTopic = os.getenv("DAPR_AGENTS_TOPIC", "agents")
conversationsTopic = os.getenv("DAPR_CONVERSATIONS_TOPIC", "conversations")

app = App()


def initialize_key_tracking(client):
    """Initializes the key tracking list in the state store."""
    # Check if the key tracking list already exists
    tracking_key = "agent_keys"
    existing_keys = client.get_state(stateStore, tracking_key).data
    if not existing_keys:
        client.save_state(stateStore, tracking_key, json.dumps([]))
        logging.info("Initialized key tracking list in state store.")


def update_key_tracking(client, key, add=True):
    """Updates the key tracking list in the state store."""
    tracking_key = "agent_keys"
    keys_data = client.get_state(stateStore, tracking_key).data
    if keys_data:
        keys_list = json.loads(keys_data)
    else:
        keys_list = []

    if add and key not in keys_list:
        keys_list.append(key)
        client.save_state(stateStore, tracking_key, json.dumps(keys_list))
        logging.info("Added key %s to tracking list.", key)
    elif not add and key in keys_list:
        keys_list.remove(key)
        client.save_state(stateStore, tracking_key, json.dumps(keys_list))
        logging.info("Removed key %s from tracking list.", key)


def saveAgentToState(agent):
    """Saves or removes an agent in the state store based on their tea amount."""
    with DaprClient() as client:
        key = f"dialogue-orchestrator:agent_{agent['id']}"  # Changed '||' to ':'
        if agent["tea_amount_ml"] > 0:
            client.save_state(stateStore, key, json.dumps(agent))
            update_key_tracking(client, key, add=True)
            logging.info("Agent %s saved to state with key %s", agent["name"], key)
        else:
            client.delete_state(stateStore, key)
            update_key_tracking(client, key, add=False)
            logging.info(
                "Agent %s removed from state due to zero tea amount", agent["name"]
            )


def chooseAgentExcluding(conversationName):
    """Selects a random agent, ensuring it is not the author of the conversation."""
    with DaprClient() as client:
        tracking_key = "agent_keys"
        keys_data = client.get_state(stateStore, tracking_key).data
        if keys_data:
            agent_keys = json.loads(keys_data)
        else:
            logging.info("No agent keys available.")
            return None

        agents = []
        for key in agent_keys:
            agent_data_response = client.get_state(stateStore, key)
            if agent_data_response.data:
                try:
                    agent_data = json.loads(agent_data_response.data)
                    if (
                        agent_data
                        and "name" in agent_data
                        and agent_data["name"] != conversationName
                    ):
                        agents.append(agent_data)
                except json.JSONDecodeError as e:
                    logging.error("Failed to decode agent data for key %s: %s", key, e)
                    continue

        if not agents:
            logging.info("No valid agents available.")
            return None

        chosen_agent = random.choice(agents)
        logging.info("Selected agent %s for response.", chosen_agent["name"])
        return chosen_agent


def invokeLlmService(agent, message):
    """Invokes the LLM service using Dapr to generate a response using the selected agent's details."""
    requestData = {
        "agent": {
            "id": agent["id"],
            "name": agent["name"],
            "description": agent["description"],
            "tea_amount_ml": agent["tea_amount_ml"],
        },
        "message": message,
    }
    with DaprClient() as d:
        try:
            resp = d.invoke_method(
                app_id="dialogue-generator",  # This must match the dapr app-id of the service you're invoking
                method_name="generate",
                http_verb="POST",
                data=json.dumps(requestData),
                content_type="application/json",  # Set the content type here
            )
            logging.info("Response from LLM service: %s", resp.text())
        except Exception as e:
            logging.error(f"Failed to invoke LLM service: {str(e)}")


@app.subscribe(pubsub_name=pubsubName, topic=agentsTopic)
def agentsSubscriber(event: v1.Event):
    """Subscriber for agent events. Updates the state store based on agent's tea amount."""
    agentData = json.loads(event.Data())
    saveAgentToState(agentData)


@app.subscribe(pubsub_name=pubsubName, topic=conversationsTopic)
def conversationsSubscriber(event: v1.Event):
    logging.info("Received conversation event.")
    conversationData = json.loads(event.Data())
    logging.info("Conversation data: %s", conversationData)
    if "name" in conversationData:
        agent = chooseAgentExcluding(conversationData["name"])
        if agent is not None:
            invokeLlmService(agent, conversationData["message"])
        else:
            logging.info("No agent selected.")
    else:
        logging.error("Name key not found in conversation data.")


if __name__ == "__main__":
    app.run(5300)

