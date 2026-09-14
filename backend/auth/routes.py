from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from auth.models import User
from auth.schemas import LoginRequest, UserCreate, UserResponse
from auth.utils import (
    COOKIE_NAME,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_token_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    data: UserCreate, response: Response, db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    print(f"Creating user with password: {data.password}")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id))
    _set_token_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(str(user.id))
    _set_token_cookie(response, token)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
