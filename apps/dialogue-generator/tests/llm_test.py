from langchain_community.llms import Ollama
import os
import json

# Set environment variables
llm_name = os.getenv('OLLAMA_LLM_NAME', 'dolphin-mixtral:8x7b-v2.6.1-q3_K_L')
llm_url = os.getenv('OLLAMA_LLM_URL', 'http://mk8s01-u22-mo.zuru.local:11434')

llm = Ollama(model=llm_name, base_url=llm_url)

def invoke_dialogue_generator(agent: dict, message: str) -> str:
    description = agent.get('description')
    latest_message = message

    prompt = f"""Character Description: {description}

    Latest Message: {latest_message}

    Context: The conversation is light-hearted and humorous, unfolding over a cup of tea. It's brief but engaging, offering a glimpse into the character's quirky personality.

    Response:"""
    
    token_count = 0
    for chunk in llm.stream(prompt):
        token_count += len(chunk.split())  # Count the words in each chunk

    response = ''.join(chunk for chunk in llm.stream(prompt))
    generated_response = response.strip()

    return generated_response

# Test the function
agent = {
    "name": "Antoain Jelliu",
    "description": "A metaphysiscs nerd.",
    "tea_amount_ml": 100
}
message = "As I sip my tea, I can't help but ponder on the intricacies of this metaphysics nerd's life. Always diving deep into the realm of abstract concepts and philosophical musings, they must have a unique perspective on our mundane, everyday problems. But today, even they found themselves knee-deep in fixing bugs - quite the relatable struggle for anyone working with technology! The contrast between their usual intellectual pursuits and these technical hiccups adds an interesting twist to this character's persona, making them even more intriguing."

print(invoke_dialogue_generator(agent, message))