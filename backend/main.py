import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from pwdlib import PasswordHash
from starlette.middleware.sessions import SessionMiddleware



BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "web-interface"

env_path = BASE_DIR / ".env"

load_dotenv(env_path)

print(BASE_DIR)



load_dotenv(BASE_DIR / "backend" / ".env")

APP_PASSWORD_HASH = os.environ["APP_PASSWORD_HASH"]


# maybe remove session_secret later as unnecessary
SESSION_SECRET = secrets.token_hex(32)


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",


    https_only=False, # for deploy turn it True
)


password_hash = PasswordHash.recommended()


# Login page

@app.get("/")
def login_page(request: Request):

    if request.session.get("authenticated"):
        return RedirectResponse("/app", status_code=303)

    return FileResponse(FRONTEND_DIR / "login.html")



# Login


@app.post("/login")
def login(
    request: Request,
    password: str = Form(...)
):

    if not password_hash.verify(
        password,
        APP_PASSWORD_HASH
    ):
        return RedirectResponse(
            "/?error=1",
            status_code=303
        )

    request.session["authenticated"] = True

    return RedirectResponse(
        "/app",
        status_code=303
    )



# Main app page


@app.get("/app")
def protected_page(request: Request):

    if not request.session.get("authenticated"):
        return RedirectResponse(
            "/",
            status_code=303
        )

    return FileResponse(
        FRONTEND_DIR / "app.html"
    )


# Logout

@app.post("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        "/",
        status_code=303
    )