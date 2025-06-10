from fastapi import FastAPI, HTTPException, Request, Form  # 🆕 Request, Form
from fastapi.responses import RedirectResponse  # 🆕 для редиректа после формы
from fastapi.staticfiles import StaticFiles  # 🆕 для статики
from fastapi.templating import Jinja2Templates  # 🆕 для шаблонов
from pydantic import BaseModel
from typing import List
from uuid import uuid4, UUID

from schemas import PodcastEpisode, EpisodeCreateRequest, GenerationRequest, GenerationResponse
from storage import episode_storage
from services.llm_client import generate_alternative_text

app = FastAPI()

# 🆕 Подключаем директорию со статикой и шаблонами
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# 🆕 HTML: Главная страница со списком эпизодов и формой добавления
@app.get("/")
def index(request: Request):
    episodes = list(episode_storage.values())
    return templates.TemplateResponse("index.html", {"request": request, "episodes": episodes})


# 🆕 HTML: Обработка формы добавления эпизода
@app.post("/create")
def create_episode_web(request: Request, title: str = Form(...), description: str = Form(...), host: str = Form(...)):
    episode_id = uuid4()
    episode = PodcastEpisode(id=episode_id, title=title, description=description, host=host)
    episode_storage[episode_id] = episode
    return RedirectResponse(url="/", status_code=302)


# ✅ REST API
@app.get("/episodes", response_model=List[PodcastEpisode])
def get_episodes():
    return list(episode_storage.values())


@app.post("/episodes", response_model=PodcastEpisode)
def create_episode(episode_data: EpisodeCreateRequest):
    episode_id = uuid4()
    episode = PodcastEpisode(id=episode_id, **episode_data.dict())
    episode_storage[episode_id] = episode
    return episode


@app.get("/episodes/{episode_id}", response_model=PodcastEpisode)
def get_episode(episode_id: UUID):
    episode = episode_storage.get(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found.")
    return episode


@app.delete("/episodes/{episode_id}")
def delete_episode(episode_id: UUID):
    if episode_id not in episode_storage:
        raise HTTPException(status_code=404, detail="Episode not found.")
    del episode_storage[episode_id]
    return {"status": "Episode deleted successfully."}


@app.post("/episodes/{episode_id}/generate_alternative", response_model=GenerationResponse)
async def generate_alternative(episode_id: UUID, request: GenerationRequest):
    episode = episode_storage.get(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found.")

    context = (
        f"Title: {episode.title}\n"
        f"Description: {episode.description}\n"
        f"Host: {episode.host}"
    )

    alternative = await generate_alternative_text(
        context=context,
        prompt=request.prompt
    )

    return GenerationResponse(
        original_episode=episode,
        target=request.target,
        prompt=request.prompt,
        generated_alternative=alternative
    )
