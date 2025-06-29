# Implements the Adaptive Project Management & Robotics Orchestration Agent.
# Manages the overall project plan and orchestrates tasks.

import asyncio
import logging
from google.adk.message import Message, MessageType
from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
# from adk_core.llm_api import llm_api_instance # Uncomment if this agent directly uses LLMs

logger = logging.getLogger(__name__)

class AdaptiveProjectManagementRoboticsOrchestrationAgent(ConstructionAgent):
    """
    Manages the overall project plan, orchestrates tasks across other agents,
    integrates data, and prepares project summaries. It's designed to adapt
    to changes and oversee project execution.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.PROJECT_MANAGEMENT,
            [
                AgentCapabilities.EXECUTION_MANAGEMENT,
                AgentCapabilities.PLANNING,
                AgentCapabilities.INTEGRATION # Integrates data from various agents
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Project Management Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Start project planning and cost estimation":
                # This is the initial trigger for project planning from the Digital Twin Agent.
                project_id = data.get("project_id")
                final_design_bundle = data.get("final_design_bundle", {})
                site_report = data.get("site_report", {})
                logger.info(f"Project Management Agent: Kicking off initial planning for {project_id}. Requesting cost estimate.")

                # This agent acts as an orchestrator. It immediately delegates the cost estimation
                # to the Cost/Supply Chain Agent.
                await asyncio.sleep(2) # Simulate some initial planning overhead
                
                await self.send_task_message(
                    AgentRoles.COST_SUPPLY_CHAIN, # Delegate to Cost/Supply Chain Agent
                    "Estimate project costs and develop procurement plan",
                    {"project_id": project_id, "final_design_bundle": final_design_bundle}, # Pass design data
                    original_sender_id=original_sender_id # Maintain traceability
                )
            elif task == "Incorporate cost and procurement data into master plan":
                # This message is received from the Cost/Supply Chain Agent after it completes its task.
                project_id = data.get("project_id")
                cost_estimate = data.get("cost_estimate", {})
                # You might also retrieve other data from internal state if needed (design_bundle, site_report)
                logger.info(f"Project Management Agent: Incorporating cost data into master plan for {project_id}.")
                
                # --- Placeholder for actual logic ---
                # In a full implementation, this agent would:
                # 1. Integrate design data (from stored state or passed data), site constraints, and the newly received cost estimates.
                # 2. Develop a detailed master project plan, including Gantt charts, critical path analysis, resource allocation schedules.
                # 3. Use an LLM (like Gemini) to identify potential schedule risks, optimize workflows for efficiency, or simulate project timelines.
                # 4. Potentially interact with Robotics Orchestration (if real-world robots are involved in construction).

                simulated_master_plan = {
                    "project_id": project_id,
                    "status": "master_plan_drafted",
                    "budget": cost_estimate.get("estimated_total_cost_usd"),
                    "timeline_weeks": 52, # Example realistic timeline for a significant project
                    "key_milestones": ["Foundation Poured", "Structural Frame Complete", "MEP Installation Begin", "Exterior Cladding Done", "Interior Finishes Complete", "Final Inspection", "Client Handover"],
                    "resource_allocation_notes": "Initial draft based on cost estimate and design complexity. Detailed resource planning to follow client approval.",
                    "risks_identified": ["Budget overrun (high material cost volatility)", "Supply chain delays (global logistics issues)", "Weather impacts (seasonal delays)", "Permitting delays"],
                    "next_step": "Present master project plan to client for approval and initiate procurement of long-lead items."
                }
                logger.info(f"Project Management Agent: Master plan drafted for {project_id}.")

                await self.send_result_message(
                    AgentRoles.CLIENT_ENGAGEMENT, # Report back to Client Engagement for overview in API response
                    {"message": f"Master project plan drafted for {project_id}. Budget: ${simulated_master_plan['budget']:,}", "plan_summary": simulated_master_plan},
                    task_id="master_plan_drafted"
                )
                
                # After drafting the plan, inform the Human-AI Collaboration agent to present it to the client.
                await self.send_task_message(
                    AgentRoles.HUMAN_COLLABORATION, # Delegate to Human-AI Collaboration Agent
                    "Present master project plan to client for approval",
                    {"project_id": project_id, "master_plan": simulated_master_plan}, # Pass the drafted plan
                    original_sender_id=original_sender_id
                )
            else:
                logger.warning(f"Project Management Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Project Management Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent would process results from, e.g., Risk/Safety, Quality Assurance, or even Human-AI Collaboration
            # regarding approval or changes.
        else:
            logger.warning(f"Project Management Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
