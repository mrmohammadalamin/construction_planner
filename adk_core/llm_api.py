# This file provides a centralized wrapper for interacting with Google's LLM APIs
# (Gemini for text, Imagen for images). Authentication is handled via
# GOOGLE_APPLICATION_CREDENTIALS environment variable.

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai.language_models import TextGenerationModel # Not directly used for gemini-1.5-flash but kept for context
from vertexai.vision_models import ImageGenerationModel
import os
import logging
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class LLMApi:
    def __init__(self):
        # Initialize Vertex AI client using environment variables
        # GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION are loaded from .env
        # GOOGLE_APPLICATION_CREDENTIALS handles authentication
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        
        if not project_id or not location:
            logger.error("GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION not set in .env file.")
            raise ValueError("Google Cloud project ID and location must be set in .env file.")

        try:
            vertexai.init(project=project_id, location=location)
            logger.info(f"Vertex AI initialized for project '{project_id}' in region '{location}'.")
        except Exception as e:
            logger.critical(f"Failed to initialize Vertex AI: {e}. Ensure GOOGLE_APPLICATION_CREDENTIALS is set and valid.", exc_info=True)
            raise

        # Initialize models
        # For text generation (Gemini)
        self.gemini_model = GenerativeModel("gemini-1.5-flash") # Using a strong, fast model
        # For image generation (Imagen)
        self.imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        logger.info("LLM models (Gemini, Imagen) initialized.")

    async def generate_text(self, prompt: str) -> str:
        """
        Generates text using the Gemini model.
        """
        logger.info(f"Generating text with Gemini for prompt: {prompt[:100]}...")
        try:
            # Use generate_content for Gemini 1.5 Flash
            response = await self.gemini_model.generate_content_async(prompt)
            # Access the text from the response's first candidate's first part
            if response and response.candidates and len(response.candidates) > 0 and \
               response.candidates[0].content and response.candidates[0].content.parts and \
               len(response.candidates[0].content.parts) > 0:
                text = response.candidates[0].content.parts[0].text
                logger.info("Gemini text generation successful.")
                return text
            else:
                logger.warning("Gemini text generation response missing content.")
                return "Error: Gemini response incomplete."
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}", exc_info=True)
            return f"Error generating text: {e}"

    async def generate_image(self, prompt: str) -> str:
        """
        Generates an image from a text prompt using the Imagen model.
        Returns base64 encoded image string.
        """
        logger.info(f"Generating image with Imagen for prompt: {prompt[:100]}...")
        try:
            # Imagen generation is synchronous for now in the SDK
            images = self.imagen_model.generate_images(
                prompt=prompt,
                number_of_images=1
            )
            # The SDK returns PIL Image objects, which need to be converted to base64.
            # In an async context, this might block, but for simplicity here we keep it.
            if images.images and len(images.images) > 0:
                buffered = BytesIO()
                images.images[0].save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                logger.info("Imagen image generation successful.")
                return img_str
            else:
                logger.warning("Imagen image generation response missing image.")
                return "Error: Imagen response incomplete."
        except Exception as e:
            logger.error(f"Error generating image with Imagen: {e}", exc_info=True)
            return f"Error generating image: {e}"

# Instantiate the LLM API wrapper globally so all agents can use it.
llm_api_instance = LLMApi()

