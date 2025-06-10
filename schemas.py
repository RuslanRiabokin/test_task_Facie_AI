from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal


class EpisodeCreateRequest(BaseModel):
    title: str = Field(..., example="Майбутнє ШІ")
    description: str = Field(..., example="Обговорюємо тренди в штучному інтелекті.")
    host: str = Field(..., example="Джо Роґан")


class PodcastEpisode(EpisodeCreateRequest):
    id: UUID


class GenerationRequest(BaseModel):
    target: Literal["title", "description"]
    prompt: str = Field(..., example="Перепиши опис для молоді.")


class GenerationResponse(BaseModel):
    original_episode: PodcastEpisode
    target: Literal["title", "description"]
    prompt: str
    generated_alternative: str
