# Implements the Predictive Cost & Supply Chain Agent.
# It estimates project costs and develops a procurement plan.

import asyncio
import logging
from google.adk.message import Message, MessageType # Corrected import

from adk_core.agents.agent import ConstructionAgent
from adk_core.agents.constants import AgentCapabilities, AgentRoles
# from adk_core.llm_api import llm_api_instance # Uncomment if this agent directly uses LLMs

logger = logging.getLogger(__name__)

class PredictiveCostSupplyChainAgent(ConstructionAgent):
    """
    Estimates project costs, analyzes material and labor requirements, and develops
    a preliminary procurement plan. It takes consolidated design data as input.
    """
    def __init__(self):
        super().__init__(
            AgentRoles.COST_SUPPLY_CHAIN,
            [
                AgentCapabilities.ANALYSIS,
                AgentCapabilities.EXECUTION_MANAGEMENT, # Related to procurement planning
                AgentCapabilities.FINANCE # Directly impacts project finance
            ]
        )
    async def on_message(self, message: Message, context: AgentContext):
        self.context = context
        logger.info(f"Cost/Supply Chain Agent received message from '{message.sender_id}': {message.payload}")
        if message.type == MessageType.REQUEST and message.receiver_id == self.id:
            task = message.payload.get("task")
            data = message.payload.get("data", {})
            original_sender_id = message.payload.get("original_sender_id")

            if task == "Estimate project costs and develop procurement plan":
                project_id = data.get("project_id")
                final_design_bundle = data.get("final_design_bundle", {}) # Consolidated design data
                logger.info(f"Cost/Supply Chain Agent: Estimating costs for project {project_id}.")

                # --- Placeholder for actual logic ---
                # In a full implementation, this agent would:
                # 1. Analyze the 'final_design_bundle' (e.g., digital twin model) to extract quantities of materials, components, and labor hours required (Quantity Take-Off).
                # 2. Access real-time cost databases or market data for material prices, labor rates, and equipment costs.
                # 3. Use an LLM (like Gemini, if uncommented above) to optimize the supply chain, identify cost-saving alternatives, or assess market volatility risks.
                # 4. Generate a detailed cost estimate and a strategic procurement plan, including preferred suppliers, lead times, and logistics.

                await asyncio.sleep(6) # Simulate work duration
                simulated_cost_estimate = {
                    "project_id": project_id,
                    "estimated_total_cost_usd": 650000 + (hash(project_id) % 50000), # Adds slight random variation for demo
                    "cost_breakdown": {
                        "materials": 300000, "labor": 250000, "equipment_rental": 50000, "contingency": 50000, "permits_fees": 15000
                    },
                    "procurement_strategy": "Prioritize local suppliers for sustainability, establish framework agreements for bulk materials, pre-order long-lead items.",
                    "cost_optimization_notes": "Explore alternative modular construction methods for interior elements. Review structural material options for cost efficiency.",
                    "status": "cost_estimation_complete"
                }
                logger.info(f"Cost/Supply Chain Agent: Completed cost estimation for {project_id}.")

                await self.send_result_message(
                    AgentRoles.CLIENT_ENGAGEMENT, # Report back to Client Engagement for overview
                    {"message": f"Cost estimate and procurement plan drafted for {project_id}.", "estimated_cost": simulated_cost_estimate["estimated_total_cost_usd"]},
                    task_id="cost_estimation_complete"
                )

                # Send the cost estimate and procurement data to the Project Management Agent.
                await self.send_task_message(
                    AgentRoles.PROJECT_MANAGEMENT,
                    "Incorporate cost and procurement data into master plan",
                    {"project_id": project_id, "cost_estimate": simulated_cost_estimate},
                    original_sender_id=original_sender_id
                )
            else:
                logger.warning(f"Cost/Supply Chain Agent: Unknown task '{task}' received by {self.id}.")
        elif message.type == MessageType.RESULT:
            logger.info(f"Cost/Supply Chain Agent received RESULT from '{message.sender_id}': {message.payload}")
            # This agent primarily produces outputs for other agents (like Project Management).
        else:
            logger.warning(f"Cost/Supply Chain Agent: Received unexpected message type '{message.type}' or receiver_id '{message.receiver_id}'.")
