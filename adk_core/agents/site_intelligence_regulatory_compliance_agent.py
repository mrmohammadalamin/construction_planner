# Implements the Site Intelligence & Regulatory Compliance Agent.
# It analyzes site data and regulatory constraints.

import json
import logging

from google.adk.message import Message, MessageType # Corrected import
from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
from adk_core.llm_api import llm_api_instance

logger = logging.getLogger(__name__)

class SiteIntelligenceRegulatoryComplianceAgent(ConstructionAgent):
    """
    Analyzes site data and regulatory constraints for a construction project.
    It simulates data retrieval (e.g., zoning, environmental risks) and uses Gemini
    to interpret common building codes and assess potential compliance challenges.
    It then prepares a site feasibility report and sends the next task to the
    Generative Architectural Design Agent.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.SITE_INTELLIGENCE,
            [
                AgentCapabilities.ANALYSIS,
                AgentCapabilities.PLANNING,
                AgentCapabilities.GEOSPATIAL_ANALYSIS,
                AgentCapabilities.REGULATORY_COMPLIANCE,
                AgentCapabilities.NATURAL_LANGUAGE_PROCESSING
            ]
        )
        # Mock data for site analysis and regulations. In a real application,
        # this would involve calling external APIs (e.g., geospatial services,
        # local government databases for zoning and building codes).
        self.mock_zoning_data = {
            "Suburban Area, London": {
                "residential": {"allowed_height_m": 12, "setbacks_m": {"front": 5, "sides": 3, "rear": 7}},
                "commercial": {"allowed_height_m": 20, "setbacks_m": {"front": 3, "sides": 1, "rear": 5}},
                "max_coverage_percent": 40,
                "environmental_risk": "Low (potential for minor soil contamination near old industrial sites)",
                "common_building_codes": "UK Building Regulations Part B (Fire Safety), Part M (Access to and use of buildings), Part L (Conservation of fuel and power)."
            },
            "Downtown, New York": {
                "residential": {"allowed_height_m": 150, "setbacks_m": {"front": 0, "sides": 0, "rear": 0}},
                "commercial": {"allowed_height_m": 300, "setbacks_m": {"front": 0, "sides": 0, "rear": 0}},
                "max_coverage_percent": 100,
                "environmental_risk": "Medium (urban heat island effect, historical underground infrastructure)",
                "common_building_codes": "NYC Building Code, ADA Compliance."
            },
            "Rural, California": {
                "residential": {"allowed_height_m": 10, "setbacks_m": {"front": 10, "sides": 5, "rear": 10}},
                "commercial": {"allowed_height_m": 15, "setbacks_m": {"front": 8, "sides": 4, "rear": 8}},
                "max_coverage_percent": 25,
                "environmental_risk": "High (wildfire risk, seismic activity, water scarcity, protected species habitats)",
                "common_building_codes": "California Building Standards Code (Title 24), Wildland-Urban Interface (WUI) codes."
            }
        }

    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Site Intelligence Agent received message from '{message.sender_id}': {message.payload}")

        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id") # Preserve original sender for traceability

            if task == "Analyze site feasibility and regulatory compliance":
                project_id = data.get("project_id")
                location = data.get("location")
                project_type = data.get("project_type")
                initial_requirements = data.get("initial_requirements", {})

                logger.info(f"Site Intelligence Agent: Starting site analysis for project {project_id} at {location} for a {project_type} building.")

                try:
                    # 1. Simulate Site Data Retrieval (replace with real API calls in production)
                    # Selects mock data based on location, defaults if not found.
                    site_info = self.mock_zoning_data.get(location, self.mock_zoning_data["Suburban Area, London"])
                    
                    zoning_rules = site_info.get(project_type, {})
                    environmental_risk = site_info.get("environmental_risk", "Unknown")
                    common_codes = site_info.get("common_building_codes", "Standard building codes apply.")

                    # 2. Use Gemini for Regulatory Interpretation and Risk Assessment Summary
                    regulatory_prompt = (
                        f"Given the following site information and common building codes for a '{location}' located project "
                        f"of type '{project_type}', summarize the key regulatory constraints and primary environmental risks. "
                        f"Focus on aspects like maximum height, setbacks, and notable code sections. "
                        f"Also, identify any potential compliance challenges given the initial requirements: {initial_requirements}. "
                        f"Site Info: {site_info}"
                        f"Format the output as a JSON object with keys like 'summary', 'compliance_challenges', 'recommendations'."
                    )
                    logger.info("Site Intelligence Agent: Calling Gemini for regulatory interpretation...")
                    gemini_regulatory_response_str = await llm_api_instance.generate_text(regulatory_prompt)

                    try:
                        gemini_regulatory_parsed = json.loads(gemini_regulatory_response_str)
                    except json.JSONDecodeError:
                        logger.error(f"Site Intelligence Agent: Gemini regulatory response was not valid JSON: {gemini_regulatory_response_str}. Using fallback data.")
                        gemini_regulatory_parsed = {
                            "summary": "Could not parse regulatory summary from AI. Manual review required.",
                            "compliance_challenges": ["AI parsing failed or response malformed."],
                            "recommendations": ["Consult local regulations directly for detailed compliance."]
                        }

                    # 3. Compile the comprehensive Site Feasibility Report
                    site_feasibility_report = {
                        "project_id": project_id,
                        "location": location,
                        "project_type": project_type,
                        "status": "initial_analysis_complete",
                        "zoning_data": {
                            "allowed_height_m": zoning_rules.get("allowed_height_m", "N/A"),
                            "setbacks_m": zoning_rules.get("setbacks_m", {}),
                            "max_coverage_percent": site_info.get("max_coverage_percent", "N/A")
                        },
                        "environmental_risk": environmental_risk,
                        "common_building_codes": common_codes,
                        "regulatory_summary_ai": gemini_regulatory_parsed.get("summary", "N/A"),
                        "compliance_challenges_ai": gemini_regulatory_parsed.get("compliance_challenges", []),
                        "site_recommendations_ai": gemini_regulatory_parsed.get("recommendations", [])
                    }
                    logger.info(f"Site Intelligence Agent: Generated Site Feasibility Report for {project_id}.")

                    # 4. Send a RESULT message back to the Client Engagement Agent.
                    # This keeps the initiating agent informed of the workflow progress.
                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT,
                        {"message": f"Site analysis complete for {project_id}.", "report_summary": site_feasibility_report["regulatory_summary_ai"]},
                        task_id="site_analysis_complete"
                    )

                    # 5. Delegate the next step: Send a TASK message to the Architectural Design Agent.
                    await self.send_task_message(
                        AgentRoles.ARCHITECTURAL_DESIGN,
                        "Generate initial architectural concepts based on feasibility",
                        {
                            "project_id": project_id,
                            "site_feasibility_report": site_feasibility_report,
                            "initial_requirements": initial_requirements
                        },
                        original_sender_id=original_sender_id # Maintain traceability
                    )

                except Exception as e:
                    logger.error(f"Site Intelligence Agent: Error during site analysis: {e}", exc_info=True)
                    error_details = f"Failed site analysis for {project_id}: {str(e)}"
                    # In case of failure, report back to the Client Engagement Agent with an error status.
                    await self.send_result_message(
                        AgentRoles.CLIENT_ENGAGEMENT,
                        {"status": "error", "agent": self.id, "details": error_details},
                        task_id="site_analysis_failed"
                    )
            else:
                logger.warning(f"Site Intelligence Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Site Intelligence Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent doesn't expect results from others in this current flow, but could
            # be extended to process data from, e.g., geospatial tools.
        else:
            logger.warning(f"Site Intelligence Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
