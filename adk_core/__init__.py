# This file marks 'adk_core' as a Python package.
# It also defines and exposes the 'root_agent' for the ADK system,
# and contains the system initialization logic.

import logging
# CORRECTED IMPORT PATH for ADK Resolver
from google.adk.resolver import Resolver

# Import individual agent classes from their new modular files
from .agents.strategic_client_engagement_agent import StrategicClientEngagementAgent
from .agents.site_intelligence_regulatory_compliance_agent import SiteIntelligenceRegulatoryComplianceAgent
from .agents.generative_architectural_design_agent import GenerativeArchitecturalDesignAgent
from .agents.integrated_systems_engineering_agent import IntegratedSystemsEngineeringAgent
from .agents.interior_experiential_design_agent import InteriorExperientialDesignAgent
from .agents.hyper_realistic_3d_digital_twin_agent import HyperRealistic3DDigitalTwinAgent
from .agents.predictive_cost_supply_chain_agent import PredictiveCostSupplyChainAgent
from .agents.adaptive_project_management_robotics_orchestration_agent import AdaptiveProjectManagementRoboticsOrchestrationAgent
from .agents.proactive_risk_safety_management_agent import ProactiveRiskSafetyManagementAgent
from .agents.ai_driven_quality_assurance_control_agent import AIDrivenQualityAssuranceControlAgent
from .agents.semantic_data_integration_ontology_agent import SemanticDataIntegrationOntologyAgent
from .agents.learning_adaptation_agent import LearningAdaptationAgent
from .agents.human_ai_collaboration_explainability_agent import HumanAICollaborationExplainabilityAgent
from .agents.sustainability_green_building_agent import SustainabilityGreenBuildingAgent
from .agents.financial_investment_analysis_agent import FinancialInvestmentAnalysisAgent
from .agents.legal_contract_management_agent import LegalContractManagementAgent
from .agents.workforce_management_hr_agent import WorkforceManagementHRAgent
from .agents.post_construction_facility_management_agent import PostConstructionFacilityManagementAgent
from .agents.public_relations_stakeholder_communication_agent import PublicRelationsStakeholderCommunicationAgent

# Import AgentRoles for referencing agent IDs
from .agents.constants import AgentRoles

logger = logging.getLogger(__name__)

# The ADK framework looks for a 'root_agent' variable at the top level
# of your agent package. This defines the primary entry point for the system.
root_agent = StrategicClientEngagementAgent()

# Global variables to hold the ADK resolver and a dictionary of all agents
adk_resolver = None
adk_agents = {} # This will store instances of all agents

async def initialize_adk_system():
    """
    Initializes the ADK Multi-Agent Construction System components.
    This function instantiates all agents and registers them with the Resolver.
    """
    logger.info("Initializing ADK Multi-Agent Construction System components...")

    global adk_resolver, adk_agents

    # Instantiate all agent classes.
    # The 'root_agent' (StrategicClientEngagementAgent) is already instantiated globally.
    adk_agents = {
        AgentRoles.CLIENT_ENGAGEMENT: root_agent, # Use the global root_agent instance
        AgentRoles.SITE_INTELLIGENCE: SiteIntelligenceRegulatoryComplianceAgent(),
        AgentRoles.ARCHITECTURAL_DESIGN: GenerativeArchitecturalDesignAgent(),
        AgentRoles.SYSTEMS_ENGINEERING: IntegratedSystemsEngineeringAgent(),
        AgentRoles.EXPERIENTIAL_DESIGN: InteriorExperientialDesignAgent(),
        AgentRoles.DIGITAL_TWIN: HyperRealistic3DDigitalTwinAgent(),
        AgentRoles.COST_SUPPLY_CHAIN: PredictiveCostSupplyChainAgent(),
        AgentRoles.PROJECT_MANAGEMENT: AdaptiveProjectManagementRoboticsOrchestrationAgent(),
        AgentRoles.RISK_SAFETY: ProactiveRiskSafetyManagementAgent(),
        AgentRoles.QUALITY_ASSURANCE: AIDrivenQualityAssuranceControlAgent(),
        AgentRoles.DATA_INTEGRATION: SemanticDataIntegrationOntologyAgent(),
        AgentRoles.LEARNING_ADAPTATION: LearningAdaptationAgent(),
        AgentRoles.HUMAN_COLLABORATION: HumanAICollaborationExplainabilityAgent(),
        AgentRoles.SUSTAINABILITY_GREEN: SustainabilityGreenBuildingAgent(),
        AgentRoles.FINANCIAL_INVESTMENT: FinancialInvestmentAnalysisAgent(),
        AgentRoles.LEGAL_CONTRACT: LegalContractManagementAgent(),
        AgentRoles.WORKFORCE_HR: WorkforceManagementHRAgent(),
        AgentRoles.POST_CONSTRUCTION_FM: PostConstructionFacilityManagementAgent(),
        AgentRoles.PUBLIC_RELATIONS_COMM: PublicRelationsStakeholderCommunicationAgent(),
    }

    # Create the ADK Resolver instance
    adk_resolver = Resolver()

    # Register each agent with the resolver. The resolver enables agents to send
    # messages to each other using their agent_id.
    for agent_id, agent_instance in adk_agents.items():
        adk_resolver.register_agent(agent_instance)

    logger.info("ADK components initialized and agents registered.")
    return adk_resolver, adk_agents