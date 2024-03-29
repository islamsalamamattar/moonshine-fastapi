from fastapi import APIRouter, HTTPException, Response, Depends, Request
from typing import List, Any
import json
from datetime import datetime
import uuid

from app.models.user import User
from app.models.interaction import Interaction
from app.core.database import DBSessionDep
from app.core.exceptions import AuthFailedException, BadRequestException, ForbiddenException, NotFoundException

from app.core.jwt import (
    decode_access_token,
    SUB, JTI, EXP,
)
from app.utils.completions_groq import (create_chat_completions)
from app.schemas.chatcompletion import (ChatCompletionResponse, ChatCompletionRequest, Message)

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

assistant_id = uuid.uuid4()

@router.post("/message", response_model=Any)
async def chat_response(
    token: str,
    message: str,
    db: DBSessionDep
):
    payload = await decode_access_token(db=db, token=token)
    user = await User.find_by_username(db=db, username=payload['sub'])

    if not user:
        raise NotFoundException(detail="User not found")

    # Your existing code
    messages = [
        {'role': "system", 'content': f"Alright, listen up! I'm your go-to pet guru, specializing in all things furry and fabulous. So, what's the scoop? You, yeah you, {user.username}, are in dire need of some golden advice for that adorable fluffball of yours, Candy, who's strutting her stuff at 8 months old. Let's make sure she's living her best life, shall we?"},
        {'role':"user", 'content':message}
        ]

    params = {
        'messages': messages,
        'model': 'mixtral-8x7b-32768',
        'stop': ['<SYS>'],
        'stream': False,
        'top_p': 0.95,
        'max_tokens': 500
    }

    # Generate chat response using OpenAI
    response = await create_chat_completions(**params)

    response_str = response.choices[0].message.content

    # Format the datetime as a string
    created_at = int(datetime.now().timestamp() * 1000)
    id = uuid.uuid4()

    # Save Interaction instance
    interaction = await Interaction.create(
        db=db,
        user_id=user.id,
        prompt=message,
        response=response.choices[0].message.content,
        model='mixtral-8x7b-32768',
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens
    )

    #current_user = await User.find_by_username(db=db, username=payload['sub'])

    reply = {
        "id": id,
        "createdAt": created_at,
        "status": "seen",
        "text": response_str,
        "type": "text"
    }
    response_author = {
        "id": assistant_id,
        "firstName": "Pet",
        "lastName": "Pal",
        "imageUrl": "https://project-moonshine.com/static/assets/img/assistant2.png"
      }
    reply["author"] = response_author
    return reply


@router.post("/history", response_model=Any)
async def chat_history(
    token: str,
    db: DBSessionDep
):
    payload = await decode_access_token(db=db, token=token)
    user = await User.find_by_username(db=db, username=payload['sub'])

    if not user:
        raise NotFoundException(detail="User not found")
    
    prompt_author = {
        "id": user.id,
        "firstName": user.firstName,
        "lastName": user.lastName,
      }

    response_author = {
        "id": assistant_id,
        "firstName": "Pet",
        "lastName": "Pal",
        "imageUrl": "https://project-moonshine.com/static/assets/img/assistant2.png"
      }

    # Format the datetime as a string
    created_at = int(datetime.now().timestamp() * 1000)

    # Save Interaction instance
    interactions = await Interaction.find_by_user_id(db=db, user_id=user.id)

    messages = []

    for interaction in interactions:


        response = {
            "id": uuid.uuid4(),
            "createdAt": created_at,
            "status": "seen",
            "text": interaction.response,
            "type": "text"
        }
        response["author"] = response_author

        messages.append(response)

        prompt = {
            "id": uuid.uuid4(),
            "createdAt": created_at,
            "status": "seen",
            "text": interaction.prompt,
            "type": "text"
        }
        prompt["author"] = prompt_author

        messages.append(prompt)

    return {'messages': messages, 'user_id': prompt_author["id"]}