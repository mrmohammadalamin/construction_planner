# Implements the Strategic Client Engagement Agent.
# This is the entry point for new client inquiries.

import json
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
from adk_core.llm_api import llm_api_instance

logger = logging.getLogger(__name__)

class StrategicClientEngagementAgent(ConstructionAgent):
    """
    The first agent in the workflow. It receives initial client inquiries from the FastAPI
    endpoint, uses Gemini to parse and refine requirements, provides an immediate acknowledgment
    back to the API, and then delegates the next step (site analysis) to the
    Site Intelligence & Regulatory Compliance Agent.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.CLIENT_ENGAGEMENT,
            [
                AgentCapabilities.HUMAN_INTERACTION,
                AgentCapabilities.PLANNING,
                AgentCapabilities.REQUIREMENT_GATHERING,
                AgentCapabilities.NATURAL_LANGUAGE_PROCESSING
            ]
        )

    async def on_message(self, message: Message, context: AgentContext):
        self.context = context # Ensure context is always updated for current message
        logger.info(f"Client Engagement Agent received message from '{message.sender_id}': {message.payload}")

        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            client_data = message.payload.get("data", {})
            # This is the original source (e.g., "fastapi_client_inquiry_endpoint")
            original_sender_id = message.sender_id

            if task == "Process new client inquiry and gather detailed requirements":
                logger.info(f"Client Engagement Agent: Processing new client inquiry for {client_data.get('client_name')}")

                try:
                    # Use Gemini to parse and refine requirements from the client inquiry
                    prompt = (
                        f"Analyze the following client inquiry for a construction project and extract key, "
                        f"structured requirements. Be precise about 'project_type', 'client_name', 'budget_range', "
                        f"'location', and 'desired_features'. Identify any ambiguities or areas requiring clarification. "
                        f"Also, suggest immediate next steps for the project lifecycle. \n\n"
                        f"Client Inquiry: {client_data}"
                        f"Format the output as a JSON object with keys like 'parsed_requirements', 'clarification_needed', 'suggested_next_steps'."
                    )
                    logger.info("Client Engagement Agent: Calling Gemini to parse requirements...")
                    gemini_response_str = await llm_api_instance.generate_text(prompt)
                    
                    # Attempt to parse Gemini's response as JSON
                    try:
                        gemini_parsed_response = json.loads(gemini_response_str)
                    except json.JSONDecodeError:
                        logger.error(f"Client Engagement Agent: Gemini response was not valid JSON: {gemini_response_str}. Using raw data as fallback.")
                        gemini_parsed_response = {
                            "parsed_requirements": client_data,
                            "clarification_needed": "Gemini could not parse inquiry, manual review needed.",
                            "suggested_next_steps": "Manual review of client inquiry."
                        }

                    parsed_requirements = gemini_parsed_response.get("parsed_requirements", client_data)
                    clarification_needed = gemini_parsed_response.get("clarification_needed", "None")
                    suggested_next_steps = gemini_parsed_response.get("suggested_next_steps", "Proceed to site analysis.")

                    logger.info(f"Client Engagement Agent: Parsed Requirements: {parsed_requirements}")
                    logger.info(f"Client Engagement Agent: Clarification Needed: {clarification_needed}")
                    logger.info(f"Client Engagement Agent: Suggested Next Steps: {suggested_next_steps}")

                    # Immediately inform the API (which is waiting on this agent's queue)
                    # that the initial processing is done. This provides a quick response to the frontend.
                    response_for_api = {
                        "status": "processing_initiated",
                        "agent": self.id,
                        "details": "Client inquiry processed. Initial data extracted. Workflow initiated.",
                        "parsed_data": parsed_requirements,
                        "clarifications": clarification_needed,
                        "workflow_suggested": suggested_next_steps
                    }
                    await self.put_response_for_api(response_for_api)

                    # Delegate the next step in the workflow to the Site Intelligence Agent
                    # Pass the original_sender_id for traceability throughout the workflow
                    await self.send_task_message(
                        AgentRoles.SITE_INTELLIGENCE,
                        "Analyze site feasibility and regulatory compliance",
                        {"project_id": "proj_" + str(hash(frozenset(client_data.items())))[:8], # Simple unique ID for the project
                         "location": parsed_requirements.get("location"),
                         "project_type": parsed_requirements.get("project_type"),
                         "initial_requirements": parsed_requirements},
                        original_sender_id=original_sender_id
                    )

                except Exception as e:
                    logger.error(f"Client Engagement Agent: Error processing inquiry: {e}", exc_info=True)
                    error_response = {
                        "status": "error",
                        "agent": self.id,
                        "details": f"Failed to process client inquiry: {str(e)}"
                    }
                    await self.put_response_for_api(error_response)
            # Handle RESULT messages coming back from other agents
            elif message.type == MessageType.RESULT:
                logger.info(f"Client Engagement Agent received RESULT from '{message.sender_id}': {message.payload}")
                # This agent acts as a central aggregator for high-level results for logging/dashboarding.
                task_id = message.payload.get("task_id")
                result_data = message.payload.get("result")
                logger.info(f"Aggregated result for task '{task_id}' from '{message.sender_id}': {result_data}")
                # If the original sender was the FastAPI endpoint and this is a final result,
                # you might want to push it back to the API's queue if a WebSocket isn't used.
                # For this setup, the API only waits for the initial response.
        else:
            logger.warning(f"Client Engagement Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
