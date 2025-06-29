# This file contains the base class for all construction agents,
# providing common functionalities and ADK integrations.

import asyncio
import logging
from typing import Dict, Any, Optional
# CORRECTED IMPORT PATH for ADK Agent, AgentContext, Message, MessageType
from google.adk.agents import Agent, AgentContext
from google.adk.messages import Message, MessageType

logger = logging.getLogger(__name__)

class ConstructionAgent(Agent):
    """
    Base class for all AI agents in the Construction AI Multi-Agent System.
    Provides common methods for initialization, message handling, and inter-agent communication.
    """
    def __init__(self, agent_id: str, capabilities: list[str]):
        super().__init__(agent_id)
        self.capabilities = capabilities
        # A queue to hold responses specifically for the FastAPI endpoint.
        # Only the agent directly responding to the API needs to use this.
        self.response_queue = asyncio.Queue()
        self.context: Optional[AgentContext] = None # Stores the ADK AgentContext when message is received
        logger.info(f"Agent '{self.id}' initialized with capabilities: {', '.join(capabilities)}")

    async def on_start(self):
        """Called when the agent starts."""
        logger.info(f"Agent '{self.id}' has started.")

    async def on_message(self, message: Message, context: AgentContext):
        """
        Default message handler for the base agent.
        Specific agent implementations will override this method to define their logic.
        """
        self.context = context # Ensure context is always set for the current message processing
        logger.info(f"Agent '{self.id}' (base) received message from '{message.sender_id}': {message.payload}")

    async def on_stop(self):
        """Called when the agent stops."""
        logger.info(f"Agent '{self.id}' has stopped.")

    async def send_task_message(self, receiver_id: str, task_description: str, data: dict = None, original_sender_id: str = None):
        """
        Helper method for an agent to send a task (REQUEST message) to another agent.
        Includes an optional `original_sender_id` for workflow traceability.
        """
        if self.context is None:
            logger.error(f"Agent '{self.id}' context not set. Cannot send message to {receiver_id}.")
            return
        payload = {"task": task_description, "data": data if data is not None else {}}
        if original_sender_id:
            payload["original_sender_id"] = original_sender_id
        message = Message(self.id, receiver_id, MessageType.REQUEST, payload)
        logger.info(f"Agent '{self.id}' sending TASK to '{receiver_id}': {task_description}")
        await self.context.send_message(message)

    async def send_result_message(self, receiver_id: str, result_data: dict, task_id: Optional[str] = None):
        """
        Helper method for an agent to send a result (RESULT message) to another agent.
        Used to communicate completion or data back up the chain or to specific agents.
        """
        if self.context is None:
            logger.error(f"Agent '{self.id}' context not set. Cannot send result message to {receiver_id}.")
            return
        payload = {"result": result_data}
        if task_id:
            payload["task_id"] = task_id
        message = Message(self.id, receiver_id, MessageType.RESULT, payload)
        logger.info(f"Agent '{self.id}' sending RESULT to '{receiver_id}'")
        await self.context.send_message(message)

    async def put_response_for_api(self, response_data: Dict[str, Any]):
        """
        Puts a response into the agent's internal queue. This is primarily used by
        the `StrategicClientEngagementAgent` to send an immediate response back
        to the FastAPI endpoint that initiated the workflow.
        """
        logger.info(f"Agent '{self.id}' putting API response in queue: {response_data.get('status')}")
        await self.response_queue.put(response_data)

    async def get_response_from_api(self, timeout: float = 90.0) -> Dict[str, Any] | None:
        """
        Retrieves a response from the agent's internal queue, with a timeout.
        This method is called by the FastAPI endpoint to get the agent's response.
        """
        try:
            response = await asyncio.wait_for(self.response_queue.get(), timeout=timeout)
            logger.info(f"Agent '{self.id}' retrieved API response from queue.")
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Agent '{self.id}' timed out waiting for response.")
            return {"status": "timeout", "agent": self.id, "details": "Agent took too long to respond."}
        except Exception as e:
            logger.error(f"Error getting response from agent '{self.id}': {e}", exc_info=True)
            return {"status": "error", "agent": self.id, "details": str(e)}
