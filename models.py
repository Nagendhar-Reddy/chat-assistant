from pydantic import BaseModel
from typing import Optional

class CustomerCreate(BaseModel):
    name: str
    age: int
    location: str
    gender: str

class CustomerResponse(BaseModel):
    name: str
    age: int
    location: str
    gender: str

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: list | dict | str