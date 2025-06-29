# Implements the Hyper-Realistic 3D Digital Twin Agent.
# It integrates all design aspects into a comprehensive 3D model.

import asyncio
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
from adk_core.llm_api import llm_api_instance

logger = logging.getLogger(__name__)

class HyperRealistic3DDigitalTwinAgent(ConstructionAgent):
    """
    Creates a comprehensive 3D digital twin of the project by integrating all design aspects
    (architectural, structural, MEP, interior, landscape). It generates photorealistic
    renders (using Imagen) and prepares the consolidated design data for subsequent agents.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.DIGITAL_TWIN,
            [
                AgentCapabilities.VISUALIZATION,
                AgentCapabilities.INTEGRATION
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Digital Twin Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Create initial 3D digital twin":
                project_id = data.get("project_id")
                architectural_concept = data.get("architectural_concept", {})
                system_design = data.get("system_design", {})
                experiential_design = data.get("experiential_design", {})
                site_report = data.get("site_report", {}) # Get site report as well for context

                logger.info(f"Digital Twin Agent: Creating digital twin for {project_id}.")
                # --- Placeholder for actual logic ---
                # This is a highly complex integration point. In a real system:
                # 1. Consolidate design data from all previous agents (architectural, structural, MEP, interior, landscape).
                # 2. Use specialized 3D modeling software APIs (e.g., BIM software) to build the comprehensive digital twin model.
                # 3. Potentially use Imagen/Veo to generate photorealistic renders or walk-through videos of the complete model.
                # 4. The output would be a viewable 3D model file (e.g., GLTF/GLB) or high-fidelity rendered assets.

                try:
                    # Generate exterior render using Imagen
                    exterior_render_prompt = (
                        f"Photorealistic 3D exterior render of a {architectural_concept.get('design_style_summary')} "
                        f"house at {site_report.get('location')} with a {experiential_design.get('landscape_features')} landscape. "
                        f"Incorporate elements from features like {architectural_concept.get('key_design_elements')}. High detail, natural lighting, daytime."
                    )
                    logger.info("Digital Twin Agent: Generating exterior render using Imagen...")
                    exterior_render_base64 = await llm_api_instance.generate_image(exterior_render_prompt)

                    # Generate interior render using Imagen
                    interior_render_prompt = (
                        f"Photorealistic 3D interior render of a {architectural_concept.get('design_style_summary')} house, "
                        f"with {experiential_design.get('interior_style')} decor and materials like {experiential_design.get('material_palette_notes')}. "
                        f"Warm lighting, cozy atmosphere, focus on living area."
                    )
                    logger.info("Digital Twin Agent: Generating interior render using Imagen...")
                    interior_render_base64 = await llm_api_instance.generate_image(interior_render_prompt)

                    simulated_twin_output = {
                        "project_id": project_id,
                        "digital_twin_url": "[https://example.com/digital_twin_model.gltf](https://example.com/digital_twin_model.gltf)", # Placeholder for actual 3D model file path
                        "exterior_render_base64": exterior_render_base64[:100] + "..." if exterior_render_base64 else "N/A", # Truncate for log/display
                        "interior_render_base64": interior_render_base64[:100] + "..." if interior_render_base64 else "N/A", # Truncate for log/display
                        "status": "initial_twin_created",
                        "details": "High-fidelity digital twin model and initial renders generated.",
                        "generated_render_prompts": {
                            "exterior": exterior_render_prompt,
                            "interior": interior_render_prompt
                        }
                    }
                    logger.info(f"Digital Twin Agent: Completed digital twin creation and renders for {project_id}.")

                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT, # Report back to Client Engagement for overview
                        {"message": f"Initial 3D Digital Twin created for {project_id}.", "details": simulated_twin_output},
                        task_id="digital_twin_complete"
                    )

                    await self.send_task_message(
                        AgentRoles.PROJECT_MANAGEMENT, # Delegate next task
                        "Start project planning and cost estimation", # This task now triggers Cost/Supply Chain via Project Management
                        {
                            "project_id": project_id,
                            "final_design_bundle": { # Bundle all consolidated design data for downstream agents
                                "architectural": architectural_concept,
                                "systems": system_design,
                                "experiential": experiential_design,
                                "digital_twin": simulated_twin_output
                            },
                            "site_report": site_report # Pass site report as well
                        },
                        original_sender_id=original_sender_id
                    )
                except Exception as e:
                    logger.error(f"Digital Twin Agent: Error generating digital twin or renders: {e}", exc_info=True)
                    error_details = f"Failed digital twin creation for {project_id}: {str(e)}"
                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT,
                        {"status": "error", "agent": self.id, "details": error_details},
                        task_id="digital_twin_failed"
                    )
            else:
                logger.warning(f"Digital Twin Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Digital Twin Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent consumes outputs from prior design agents and produces a consolidated twin.
        else:
            logger.warning(f"Digital Twin Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
