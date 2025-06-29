# Implements the Generative Architectural Design Agent.
# It generates design concepts and visuals.

import json
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
from adk_core.llm_api import llm_api_instance

logger = logging.getLogger(__name__)

class GenerativeArchitecturalDesignAgent(ConstructionAgent):
    """
    Generates initial architectural concepts and visual sketches using Gemini and Imagen.
    It receives project requirements and site feasibility data, interprets them
    to propose a design concept, generates a conceptual image, and then delegates
    the next task (systems engineering) to the Integrated Systems Engineering Agent.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.ARCHITECTURAL_DESIGN,
            [
                AgentCapabilities.DESIGN,
                AgentCapabilities.VISUALIZATION,
                AgentCapabilities.NATURAL_LANGUAGE_PROCESSING
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Architectural Design Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Generate initial architectural concepts based on feasibility":
                project_id = data.get("project_id")
                site_report = data.get("site_feasibility_report", {})
                initial_requirements = data.get("initial_requirements", {})

                logger.info(f"Architectural Design Agent: Generating concepts for project {project_id} based on site report and requirements.")

                try:
                    # 1. Use Gemini to interpret design brief, site constraints, and propose a concept
                    design_prompt = (
                        f"Based on the following site feasibility report and initial client requirements, "
                        f"propose an architectural concept. Consider the project type '{initial_requirements.get('project_type')}' "
                        f"and desired features '{initial_requirements.get('desired_features')}', adhering to "
                        f"zoning rules like max height {site_report.get('zoning_data',{}).get('allowed_height_m', 'N/A')}m. "
                        f"Summarize the proposed style, key design elements, and how it addresses site constraints. "
                        f"Site Report: {json.dumps(site_report)}\nInitial Requirements: {json.dumps(initial_requirements)}\n"
                        f"Format output as JSON with keys 'design_summary', 'key_elements', 'considerations'."
                    )
                    logger.info("Architectural Design Agent: Calling Gemini for design brief interpretation...")
                    gemini_design_response_str = await llm_api_instance.generate_text(design_prompt)
                    try:
                        gemini_design_parsed = json.loads(gemini_design_response_str)
                    except json.JSONDecodeError:
                        logger.error(f"Architectural Design Agent: Gemini design response was not valid JSON: {gemini_design_response_str}. Using fallback data.")
                        gemini_design_parsed = {
                            "design_summary": "Could not parse design summary from AI. Manual design review needed.",
                            "key_elements": ["Unspecified"],
                            "considerations": ["Manual design. AI parsing failed or response malformed."]
                        }

                    # 2. Use Imagen to generate a preliminary visual sketch based on the concept
                    image_prompt = (
                        f"Architectural sketch of a {initial_requirements.get('project_type')} house in {site_report.get('location')} "
                        f"with {initial_requirements.get('desired_features')} and a {gemini_design_parsed.get('design_summary')} style. "
                        f"Exterior view, clear daylight."
                    )
                    logger.info("Architectural Design Agent: Calling Imagen for conceptual render...")
                    image_base64 = await llm_api_instance.generate_image(image_prompt)
                    
                    simulated_design_concept = {
                        "project_id": project_id,
                        "design_style_summary": gemini_design_parsed.get("design_summary"),
                        "key_design_elements": gemini_design_parsed.get("key_elements", []),
                        "site_considerations_addressed": gemini_design_parsed.get("considerations", []),
                        "conceptual_render_base64": image_base64[:100] + "..." if image_base64 else "N/A", # Truncate for log/display
                        "floor_plan_url": "https://placehold.co/600x400/FF0000/FFFFFF?text=Conceptual_Floor_Plan", # Placeholder for a generated floor plan image
                        "exterior_render_url": "https://placehold.co/600x400/0000FF/FFFFFF?text=Conceptual_Exterior_Render" # Placeholder for a generated exterior render
                    }
                    logger.info(f"Architectural Design Agent: Generated concepts for {project_id}.")

                    # 3. Send result back to the Client Engagement Agent for logging/overview
                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT,
                        {"message": f"Architectural concepts generated for {project_id}.", "design_summary": simulated_design_concept["design_style_summary"]},
                        task_id="architectural_concepts_generated"
                    )

                    # 4. Delegate the next step: Send a TASK message to the Systems Engineering Agent.
                    await self.send_task_message(
                        AgentRoles.SYSTEMS_ENGINEERING,
                        "Develop structural and MEP preliminary designs",
                        {
                            "project_id": project_id,
                            "architectural_concept": simulated_design_concept,
                            "site_report": site_report
                        },
                        original_sender_id=original_sender_id
                    )

                except Exception as e:
                    logger.error(f"Architectural Design Agent: Error during design generation: {e}", exc_info=True)
                    error_details = f"Failed architectural design for {project_id}: {str(e)}"
                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT,
                        {"status": "error", "agent": self.id, "details": error_details},
                        task_id="architectural_design_failed"
                    )
            else:
                logger.warning(f"Architectural Design Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Architectural Design Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent does not expect results from other agents in this current flow,
            # but could be extended to, e.g., receive feedback from Quality Assurance.
        else:
            logger.warning(f"Architectural Design Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
