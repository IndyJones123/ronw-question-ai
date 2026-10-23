"""Model request/response API login (pydantic v2)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    # info device dari aplikasi desktop: hostname, os, user, python, layar
    device: dict[str, Any] = Field(default_factory=dict)


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    is_active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # detik
    user: UserOut


class LoginLogOut(BaseModel):
    id: int
    username: str
    success: bool
    reason: str
    device: dict[str, Any]
    ip: str
    user_agent: str
    created_at: str


class HealthOut(BaseModel):
    status: str
    db: bool
