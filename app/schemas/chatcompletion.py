from typing import List, Optional, Dict
from pydantic import BaseModel

class Message(BaseModel):
    content: str
    role: str
    function_call: Optional[str]
    tool_calls: Optional[List[str]]

class Choice(BaseModel):
    finish_reason: str
    index: int
    logprobs: Optional[dict]
    message: Message

class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class ChatCompletion(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    system_fingerprint: Optional[str]
    usage: Usage
