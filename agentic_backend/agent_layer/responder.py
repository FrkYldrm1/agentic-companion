# responder.py (Agent Layer)

from integration_layer.llm_client import LLMClient

llm = LLMClient()


async def generate_agent_reply(message: str) -> str:
    #import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_agent_reply(message: str) -> str:
    try:
        logger.info(f"Received message: {message}")
        response = llm.get_response(message)
        logger.info(f"Generated response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Error generating response"return llm.get_response(message)
    return "Maybe you should kill yourself!"