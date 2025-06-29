# Implements the Human-AI Collaboration & Explainability Agent.
# It facilitates human oversight and communication.

import asyncio
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
# from adk_core.llm_api import llm_api_instance # Uncomment if this agent directly uses LLMs

logger = logging.getLogger(__name__)

class HumanAICollaborationExplainabilityAgent(ConstructionAgent):
    """
    Facilitates effective communication and collaboration between human stakeholders
    (clients, project managers, engineers) and the AI agent system. It provides
    explanations of AI decisions, interfaces for human oversight, and channels for feedback.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.HUMAN_COLLABORATION,
            [
                AgentCapabilities.HUMAN_INTERACTION,
                AgentCapabilities.INTEGRATION # To integrate with human-facing dashboards/communication channels
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Human-AI Collaboration Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Present master project plan to client for approval":
                project_id = data.get("project_id")
                master_plan = data.get("master_plan", {})
                logger.info(f"Human-AI Collaboration Agent: Presenting master plan for {project_id} to client for approval.")
                
                # --- Placeholder for actual logic ---
                # In a real production system, this would:
                # 1. Trigger a UI update on a client-facing dashboard.
                # 2. Send an email notification with a summary of the plan.
                # 3. Prepare an interactive presentation (possibly with generated visuals) for human review.
                # 4. Use an LLM to generate clear, concise explanations of complex plan elements.
                # 5. Provide mechanisms for human approval or feedback (e.g., via a callback endpoint).

                final_summary = {
                    "message": f"Project '{project_id}' planning complete and ready for client approval.",
                    "final_budget_estimate": master_plan.get("budget"),
                    "timeline_overview": f"{master_plan.get('timeline_weeks')} weeks",
                    "key_milestones": master_plan.get("key_milestones"),
                    "next_action_for_human": "Review and approve master plan via the client dashboard or your designated communication channel."
                }
                await asyncio.sleep(2) # Simulate time for presentation/review
                logger.info(f"Human-AI Collaboration Agent: Ready for human approval for {project_id}.")

                # Send this final summary back to the Client Engagement Agent.
                # The Client Engagement Agent is responsible for the API interaction in this demo,
                # so it will handle the final logging/reporting back to the initial FastAPI call.
                await self.send_result_message(
                    AgentRoles.CLIENT_ENGAGEMENT, # Sending back to Client Engagement
                    final_summary,
                    task_id="master_plan_presented_for_approval"
                )
                
            else:
                logger.warning(f"Human-AI Collaboration Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Human-AI Collaboration Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent would typically receive human feedback or approval status from a UI.
        else:
            logger.warning(f"Human-AI Collaboration Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
