from dotenv import load_dotenv
import os
import json
import logging
import copy
from typing import List, Any
from groq import AsyncGroq
import openai
from sse_starlette import EventSourceResponse
import aitertools
from app.schemas.chatcompletion import ChatCompletionResponse, ChatCompletionRequest
from fastapi.encoders import jsonable_encoder

# Load environment variables from the .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "sk-XXXX"

# Setup Error handling
class OpenAIError(Exception):
    pass

def handle_openai_error(e):
    logging.error(f"OpenAI API Error: {e}")
    raise OpenAIError(f"OpenAI API Error: {e}")

# Using Chat Completions API
async def create_chat_completions(
        messages: List[str],
        model: str,
        stop: List[str],
        stream: bool,
        top_p: float,
        max_tokens: int
):
    # Set your OpenAI API key & API URL
    client = AsyncGroq(
        api_key=GROQ_API_KEY
    )

    try:
        # Make the API request and return the full response or yield the response stream
        response = await client.chat.completions.create(
            messages=messages,
            model=model
        )
        return response
    except:
        # Error handling
        raise Exception(f"Error making API request: {messages}")
