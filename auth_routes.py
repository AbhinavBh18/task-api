from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import AuthApiError
from supabase_client import supabase
from fastapi import APIRouter, HTTPException, Depends, Response
from auth import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    email: str | None = None
    password: str | None = None


def check_fields(body: Credentials):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required")


@router.post("/signup", status_code=201, summary="Create an account")
def signup(body: Credentials):
    check_fields(body)
    try:
        res = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=e.message)

    user = res.user
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        }
    }


@router.post("/login", summary="Log in and get a JWT")
def login(body: Credentials):
    check_fields(body)
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except AuthApiError as e:
        print(f"login failed: {e.code} - {e.message}")
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    session = res.session
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer",
        "expires_in": session.expires_in,
    }


@router.post(
    "/logout",
    status_code=204,
    summary="Log out",
    description="Ends the session. Requires a valid access token.",
    responses={401: {"description": "Access token missing, invalid or expired"}},
)
def logout(user=Depends(get_current_user)):
    supabase.auth.sign_out()
    return Response(status_code=204)





class Credentials(BaseModel):
    email: str | None = None
    password: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"email": "user@example.com", "password": "password123"}]
        }
    }