# This is the main FastAPI application file. It sets up the server,
# defines API endpoints, and orchestrates the ADK agent system.

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv # Used to load environment variables from .env
import os
import logging
from typing import Dict, Any, Optional

# Load environment variables from .env file at the start
load_dotenv()

# Set up logging for FastAPI to see detailed operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import ADK components and LLM API.
# 'initialize_adk_system' is now in adk_core/__init__.py
# 'AgentRoles' is in adk_core/agents/constants.py
from adk_core import initialize_adk_system, adk_agents # Import adk_agents directly from adk_core __init__.py
from adk_core.agents.constants import AgentRoles
from adk_core.agents.base_agent import ConstructionAgent # For type hinting ConstructionAgent
from adk_core.llm_api import llm_api_instance # Import the globally instantiated LLM API

# Global variables to hold the ADK resolver. adk_agents is imported from adk_core.
adk_resolver = None # This will be set by initialize_adk_system

# --- FastAPI Models for Request/Response ---
# These Pydantic models define the structure of data sent to and received from your API.
class ClientRequest(BaseModel):
    """Defines the structure for a new client inquiry."""
    project_type: str
    client_name: str
    budget_range: str
    location: str
    desired_features: list[str]
    initial_ideas_url: Optional[str] = None # Optional field

class AgentResponse(BaseModel):
    """
    Defines the general structure for responses from the agent system.
    This model is flexible to accommodate various outputs from different agents
    in the workflow.
    """
    status: str
    agent: str
    details: Dict[str, Any]
    # Optional fields that might be populated by the Client Engagement Agent's
    # initial response or other aggregated results.
    parsed_data: Optional[Dict[str, Any]] = None
    clarifications: Optional[Any] = None
    workflow_suggested: Optional[Any] = None
    # For a truly complex production app, you might use WebSockets for real-time
    # progress updates, or a more elaborate structure for aggregated results.


# --- FastAPI Lifespan Context Manager ---
# This function handles startup and shutdown logic for your FastAPI application.
# It's crucial for initializing and cleaning up the ADK agent system.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application lifespan.
    Initializes and starts ADK agents on startup, stops them on shutdown.
    """
    global adk_resolver # adk_agents is imported from adk_core and updated there
    logger.info("FastAPI app startup: Initializing ADK system...")
    try:
        # Initialize the ADK system, which registers all agents with the resolver
        # and populates the adk_agents dictionary in adk_core.
        adk_resolver_instance, _ = await initialize_adk_system()
        adk_resolver = adk_resolver_instance # Store the resolver instance
        # Start all registered agents, allowing them to begin processing messages
        await adk_resolver.start_all_agents()
        logger.info("ADK agents started successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize or start ADK agents: {e}", exc_info=True)
        # If ADK initialization fails, the application cannot run, so raise an error
        raise RuntimeError(f"Backend startup failed: {e}")

    yield # The application will run here

    logger.info("FastAPI app shutdown: Stopping ADK agents...")
    if adk_resolver:
        # Stop all ADK agents gracefully on application shutdown
        await adk_resolver.stop_all_agents()
        logger.info("ADK agents stopped successfully.")
    else:
        logger.warning("ADK resolver not initialized during shutdown.")

# Initialize FastAPI app with the lifespan manager
app = FastAPI(
    title="Construction AI Multi-Agent System",
    description="Backend for managing construction projects with ADK agents and Google AI.",
    version="1.0.0",
    lifespan=lifespan # Assign the lifespan context manager
)

# --- FastAPI Endpoints ---

@app.get("/")
async def read_root():
    """Root endpoint for a basic health check."""
    return {"message": "Welcome to the Construction AI Multi-Agent System API!"}

@app.post("/client_inquiry", response_model=AgentResponse)
async def handle_client_inquiry(request: ClientRequest):
    """
    Endpoint to receive a new client inquiry.
    This endpoint acts as the entry point for the multi-agent workflow.
    It sends the inquiry to the Strategic Client Engagement Agent (the root_agent)
    and waits for an initial acknowledgment/summary.
    """
    # Check if the ADK system is fully initialized and agents are running
    # adk_agents is now imported directly from adk_core/__init__.py
    if adk_resolver is None or not adk_agents:
        raise HTTPException(status_code=503, detail="ADK system not initialized or agents not running. Please check backend logs for startup errors.")

    # Get a reference to the Strategic Client Engagement Agent (which is also the root_agent)
    client_engagement_agent = adk_agents.get(AgentRoles.CLIENT_ENGAGEMENT)
    if not client_engagement_agent:
        raise HTTPException(status_code=500, detail=f"Agent '{AgentRoles.CLIENT_ENGAGEMENT}' not found or not registered during startup.")

    logger.info(f"Received client inquiry from external source. Forwarding to {AgentRoles.CLIENT_ENGAGEMENT}.")

    try:
        # Send the client inquiry as a task message to the Client Engagement Agent.
        # The agent will process this and put an initial response into its queue
        # for this FastAPI endpoint to pick up immediately.
        # It will then asynchronously send a task to the next agent (Site Intelligence)
        # to continue the workflow in the background.
        await client_engagement_agent.send_task_message(
            AgentRoles.CLIENT_ENGAGEMENT, # Sending to itself as the entry point
            "Process new client inquiry and gather detailed requirements",
            request.dict(), # Convert Pydantic model to dict
            original_sender_id="fastapi_client_inquiry_endpoint" # Track the original source
        )

        # Wait for the initial response from the Client Engagement Agent.
        # This makes the API call synchronous for the client to get an immediate acknowledgment
        # while the rest of the agent workflow proceeds asynchronously.
        response = await client_engagement_agent.get_response_from_api(timeout=120.0) # Increased timeout for potentially long ops

        if response and response.get("status") == "timeout":
            logger.warning(f"Client inquiry processing timed out for request: {request.client_name}")
            raise HTTPException(status_code=504, detail="Agent processing timed out. The request is still being processed in the background, but no immediate full response was available.")
        elif response and response.get("status") == "error":
            logger.error(f"Error response from agent for request: {request.client_name}, Details: {response.get('details')}")
            raise HTTPException(status_code=500, detail=f"Agent error during inquiry processing: {response.get('details')}")
        elif not response:
            logger.error(f"No response received from client engagement agent for request: {request.client_name}")
            raise HTTPException(status_code=500, detail="No initial response received from agent after inquiry submission.")

        return AgentResponse(**response) # Return the initial response to the frontend

    except HTTPException: # Re-raise FastAPI HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unhandled error in FastAPI /client_inquiry endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error processing inquiry: {e}")


# --- Direct LLM Interaction Endpoints (for testing or direct use) ---
# These endpoints allow direct access to Gemini/Imagen without going through agents.

@app.post("/generate_text")
async def generate_text_endpoint(prompt_data: Dict[str, str]):
    """
    Endpoint to directly generate text using the Gemini model.
    """
    prompt = prompt_data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required to generate text.")

    logger.info(f"Direct text generation request for prompt: {prompt[:100]}...")
    text = await llm_api_instance.generate_text(prompt)
    if text.startswith("Error:"):
        raise HTTPException(status_code=500, detail=text)
    return {"generated_text": text}

@app.post("/generate_image")
async def generate_image_endpoint(prompt_data: Dict[str, str]):
    """
    Endpoint to directly generate an image using the Imagen model.
    Returns base64 encoded image data.
    """
    prompt = prompt_data.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required to generate an image.")

    logger.info(f"Direct image generation request for prompt: {prompt[:100]}...")
    image_base64 = await llm_api_instance.generate_image(prompt)
    if image_base64.startswith("Error:"):
        raise HTTPException(status_code=500, detail=image_base64)
    return {"generated_image_base64": image_base64}

