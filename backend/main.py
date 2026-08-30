import os
import secrets
from pathlib import Path

import asyncio
import uuid
from dataclasses import dataclass, field

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from pwdlib import PasswordHash
from starlette.middleware.sessions import SessionMiddleware

from .ollama_engine import OllamaEngine



BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "web-interface"

env_path = BASE_DIR / ".env"

load_dotenv(env_path)

print(BASE_DIR)



load_dotenv(BASE_DIR / "backend" / ".env")

APP_PASSWORD_HASH = os.environ["APP_PASSWORD_HASH"]


# maybe remove session_secret later as unnecessary
SESSION_SECRET = secrets.token_hex(32)

# Queque

@dataclass
class GenerationJob:
    job_id: str
    prompt: str
    status: str = "queued"
    result: str | None = None
    error: str | None = None

generation_queue = asyncio.Queue()
jobs = {}
queue_lock = asyncio.Lock()

# Ollama engine get and process the request to generate

ollama_engine = OllamaEngine()


async def generation_worker():

    while True:

        job_id = await generation_queue.get()

        job = jobs[job_id]

        job.status = "processing"

        try:
            ollama_engine.set_model("phi4-mini")

            response = await asyncio.to_thread(
                ollama_engine.process_prompt,
                "",
                job.prompt
            )

            job.result = response
            job.status = "completed"

        except Exception as e:
            job.error = str(e)
            job.status = "failed"

        finally:
            generation_queue.task_done()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generation_worker())

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

# display instructions

INSTRUCTION_PATH = BASE_DIR / "instruction.txt"

if INSTRUCTION_PATH.exists():
    with open(INSTRUCTION_PATH, "r", encoding="utf-8") as f:
        text_to_display = f.read()
else:
    text_to_display = ""

@app.get("/instruction")
def get_data(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse("/", status_code=303)

    return {
        "text": text_to_display
    }



@app.get("/job/{job_id}")
async def get_job(job_id: str, request: Request):

    if not request.session.get("authenticated"):
        return RedirectResponse("/", status_code=303)

    job = jobs.get(job_id)

    if job is None:
        return {
            "status": "not_found"
        }

    if job.status == "queued":

        queued_ids = list(generation_queue._queue)

        try:
            position = queued_ids.index(job_id)
        except ValueError:
            position = 0

        processing_count = sum(
            1
            for existing_job in jobs.values()
            if existing_job.status == "processing"
        )

        return {
            "status": "queued",
            "users_ahead": position + processing_count
        }

    if job.status == "processing":
        return {
            "status": "processing",
            "users_ahead": 0
        }

    if job.status == "completed":
        return {
            "status": "completed",
            "result": job.result
        }

    if job.status == "failed":
        return {
            "status": "failed",
            "error": job.error
        }


@app.post("/process_prompt")
async def process_prompt(
    request: Request,
    text: str = Form(...)
):

    if not request.session.get("authenticated"):
        return RedirectResponse("/", status_code=303)

    job_id = str(uuid.uuid4())

    job = GenerationJob(
        job_id=job_id,
        prompt=text
    )

    jobs[job_id] = job

    # Number already waiting / processing
    users_ahead = generation_queue.qsize()

    # If Ollama is currently processing somebody,
    # count that person too.
    processing_count = sum(
        1
        for existing_job in jobs.values()
        if existing_job.status == "processing"
    )

    users_ahead += processing_count

    await generation_queue.put(job_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "users_ahead": users_ahead
    }