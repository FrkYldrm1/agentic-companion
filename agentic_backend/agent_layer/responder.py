# responder.py (Agent Layer)

from integration_layer.llm_client import LLMClient

llm = LLMClient()


async def generate_agent_reply(message: str) -> str:
    #return llm.get_response(message)
    return "Maybe you should kill yourself!"