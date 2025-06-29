# Implements the Interior Experiential Design Agent.
# It focuses on interior layouts, material palettes, and landscape design.

import asyncio
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles

logger = logging.getLogger(__name__)

class InteriorExperientialDesignAgent(ConstructionAgent):
    """
    Focuses on designing the interior spaces and surrounding landscape to enhance user experience.
    It considers architectural concepts and client features to propose aesthetic and functional designs.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.EXPERIENTIAL_DESIGN,
            [
                AgentCapabilities.DESIGN,
                AgentCapabilities.VISUALIZATION
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Experiential Design Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Develop interior and landscape designs":
                project_id = data.get("project_id")
                architectural_concept = data.get("architectural_concept", {}) # Data from Architectural Agent
                # systems_design = data.get("system_design", {}) # Could also consider structural/MEP constraints
                
                logger.info(f"Experiential Design Agent: Starting interior/landscape design for {project_id}.")
                
                # --- Placeholder for actual logic ---
                # In a full implementation, this agent would:
                # 1. Interpret client's desired features (e.g., "modern design", "cozy atmosphere", "minimalist") using Gemini for stylistic direction.
                # 2. Design interior layouts, material palettes (flooring, walls, finishes), lighting schemes, and furniture arrangements.
                # 3. Design landscape elements (gardens, pathways, outdoor seating, water features) to complement the architecture and site.
                # 4. Potentially use Imagen to generate interior/exterior visual mood boards or conceptual renders of key spaces.

                await asyncio.sleep(5) # Simulate work duration
                simulated_experiential_design = {
                    "project_id": project_id,
                    "interior_style": "Minimalist, Biophilic",
                    "landscape_features": "Zen garden, patio with fire pit, native plant landscaping",
                    "material_palette_notes": "Natural wood, light stone, muted colors; emphasis on sustainable and locally sourced materials.",
                    "mood_board_url": "https://placehold.co/600x400/996633/FFFFFF?text=Interior_Mood_Board", # Placeholder for Imagen output
                }
                logger.info(f"Experiential Design Agent: Completed interior/landscape design for {project_id}.")

                await self.send_result_message(
                    AgentRoles.CLIENT_ENGAGEMENT, # Report back to Client Engagement for overview
                    {"message": f"Interior and landscape designs drafted for {project_id}.", "details": simulated_experiential_design},
                    task_id="experiential_design_complete"
                )

                await self.send_task_message(
                    AgentRoles.DIGITAL_TWIN, # Delegate next task
                    "Create initial 3D digital twin",
                    {
                        "project_id": project_id,
                        "architectural_concept": architectural_concept,
                        "system_design": data.get("system_design", {}), # Pass along systems design too
                        "experiential_design": simulated_experiential_design
                    },
                    original_sender_id=original_sender_id
                )
            else:
                logger.warning(f"Experiential Design Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Experiential Design Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent primarily acts on inputs from previous stages and delegates forward.
            # Could be extended to receive feedback, e.g., from Human-AI Collaboration.
        else:
            logger.warning(f"Experiential Design Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
