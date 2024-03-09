from fastapi import APIRouter, HTTPException, Response, Depends, Request
from typing import List, Any
import json
from datetime import datetime
import uuid

from app.models.user import User
from app.core.database import DBSessionDep
from app.core.exceptions import AuthFailedException, BadRequestException, ForbiddenException, NotFoundException

from app.core.jwt import (
    decode_access_token,
    SUB, JTI, EXP,
)
from app.utils.completions_groq import (
    create_chat_completions,
    generate_chat_response_stream

)
from app.schemas.chatcompletion import ChatCompletion

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/generate/", response_model=ChatCompletion)
async def generate_chat_response(
    token: str,
    db: DBSessionDep,
    messages: List[dict] = None,  # Assuming the messages format is provided in the request body
):
    """
    Generate a chat response using the OpenAI API.
    """
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    try:
        # Assuming messages are provided in the request body
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Generate chat response using OpenAI
        response = await create_chat_completions(messages=messages)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/stream", response_model=ChatCompletion)
async def stream_chat_response(
    token: str,
    db: DBSessionDep,
    messages: List[dict] = None,
):
    """
    Generate a chat response using the OpenAI API.
    """
    payload = await decode_access_token(token=token, db=db)
    user = await User.find_by_username(db=db, username=payload[SUB])
    print("=======================================")
    print(user.username)
    if not user:
        raise NotFoundException(detail="User not found")

    try:
        # Assuming messages are provided in the request body
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Generate chat response using OpenAI
        response = await generate_chat_response_stream(messages=messages)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    


@router.post("/app", response_model=Any)
async def stream_chat_response(
    token: str,
    message: str,
    db: DBSessionDep
):
    username = "Salayem"
        # Your existing logic here...
    messages = [
        {
            "role": "system",
            "content": f"You are an AI assistant expert in pets. you are helping the user {username} to take care of his golden retriever named Candy. Candy is 8 months old."    
        }
    ]
    messages.append({"role": "user", "content": message})


    # Generate chat response using OpenAI
    response = await create_chat_completions(messages=messages)
        
    response_str = response.choices[0].message.content

    # Format the datetime as a string
    created_at = int(datetime.now().timestamp() * 1000)
    id = uuid.uuid4()
    reply = {
      "author": {
        "id": "4c2307ba-3d40-442f-b1ff-b271f6390",
        "firstName": "Pet",
        "lastName": "Pals",
        "imageUrl": "http://project-moonshine.com/static/assets/img/assistant.png"
      },
      "id": id,
      "createdAt": created_at,
      "status": "seen",
      "text": response_str,
      "type": "text"
    }
    return reply


@router.post("/messages", response_model=Any)
async def stream_chat_response(
    request: Request,
    db: DBSessionDep
):
    
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        token = data.get("token", "")
        
        '''
        try:
            payload = await decode_access_token(token=token, db=db)
        except:
            return "Token error"
        if payload:
            user = await User.find_by_username(db=db, username=payload[SUB])
        '''
        username = "Salayem"
        # Your existing logic here...
        messages = [
            {
                "role": "system",
                "content": f"You are an AI assistant expert in pets. you are helping the user {username} to take care of his golden retriever named Candy. Candy is 8 months old."    
            }
        ]
        messages.append({"role": "user", "content": prompt})
        
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt provided")

        # Generate chat response using OpenAI
        response = await create_chat_completions(messages=messages)
        
        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")