# Implements the Integrated Systems Engineering Agent.
# It develops preliminary structural and MEP designs.

import asyncio
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles

logger = logging.getLogger(__name__)

class IntegratedSystemsEngineeringAgent(ConstructionAgent):
    """
    Develops preliminary structural and MEP (Mechanical, Electrical, Plumbing) designs
    based on architectural concepts and site reports.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.SYSTEMS_ENGINEERING,
            [
                AgentCapabilities.DESIGN,
                AgentCapabilities.ANALYSIS
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Systems Engineering Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Develop structural and MEP preliminary designs":
                project_id = data.get("project_id")
                architectural_concept = data.get("architectural_concept", {})
                site_report = data.get("site_report", {})
                logger.info(f"Systems Engineering Agent: Starting preliminary structural and MEP design for {project_id}.")
                
                # --- Placeholder for actual logic ---
                # In a full implementation, this agent would:
                # 1. Analyze architectural concepts and site reports for structural and MEP implications.
                # 2. Design preliminary structural elements (beams, columns, foundations) considering load, materials, seismic data.
                # 3. Design preliminary MEP (Mechanical, Electrical, Plumbing) systems, including HVAC, electrical layouts, plumbing schematics.
                # 4. Potentially use Gemini to summarize design risks, optimize material usage for structural integrity, or identify energy-saving MEP configurations.

                await asyncio.sleep(5) # Simulate work duration
                simulated_system_design = {
                    "project_id": project_id,
                    "structural_design_status": "preliminary_complete",
                    "mep_design_status": "preliminary_complete",
                    "structural_notes": "Reinforced concrete, seismic considerations applied based on site analysis.",
                    "mep_notes": "Energy-efficient HVAC, smart lighting system proposed, considering energy regulations.",
                    "design_conflicts_detected": False # In a real system, Gemini could help identify these by comparing architectural with systems designs.
                }
                logger.info(f"Systems Engineering Agent: Completed preliminary design for {project_id}.")

                await self.send_result_message(
                    AgentRoles.CLIENT_ENGAGEMENT, # Report back to Client Engagement for high-level overview
                    {"message": f"Structural and MEP preliminary designs complete for {project_id}.", "details": simulated_system_design},
                    task_id="systems_engineering_complete"
                )

                await self.send_task_message(
                    AgentRoles.EXPERIENTIAL_DESIGN, # Delegate next task
                    "Develop interior and landscape designs",
                    {
                        "project_id": project_id,
                        "system_design": simulated_system_design,
                        "architectural_concept": architectural_concept,
                        "site_report": site_report # Pass along relevant data for the next agent
                    },
                    original_sender_id=original_sender_id
                )
            else:
                logger.warning(f"Systems Engineering Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Systems Engineering Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent typically consumes data from Architectural Design and produces its own.
            # It might receive results from sub-agents if complex sub-tasks are delegated.
        else:
            logger.warning(f"Systems Engineering Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
