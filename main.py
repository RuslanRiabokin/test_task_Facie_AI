from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4, UUID

from schemas import PodcastEpisode, EpisodeCreateRequest, GenerationRequest, GenerationResponse
from storage import episode_storage
from services.llm_client import generate_alternative_text

app = FastAPI()


@app.get("/episodes", response_model=List[PodcastEpisode])
def get_episodes():
    """
    Retrieve all podcast episodes.

    Returns:
        List of PodcastEpisode objects.
    """
    return list(episode_storage.values())


@app.post("/episodes", response_model=PodcastEpisode)
def create_episode(episode_data: EpisodeCreateRequest):
    """
    Create a new podcast episode.

    Args:
        episode_data: The episode data provided by the client.

    Returns:
        The created PodcastEpisode object.
    """
    episode_id = uuid4()
    episode = PodcastEpisode(id=episode_id, **episode_data.dict())
    episode_storage[episode_id] = episode
    return episode


@app.get("/episodes/{episode_id}", response_model=PodcastEpisode)
def get_episode(episode_id: UUID):
    """
    Retrieve a specific episode by ID.

    Args:
        episode_id: UUID of the requested episode.

    Returns:
        The matching PodcastEpisode object.

    Raises:
        HTTPException 404 if not found.
    """
    episode = episode_storage.get(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found.")
    return episode


@app.delete("/episodes/{episode_id}")
def delete_episode(episode_id: UUID):
    """
    Delete a specific episode by ID.

    Args:
        episode_id: UUID of the episode to delete.

    Returns:
        Success message.

    Raises:
        HTTPException 404 if not found.
    """
    if episode_id not in episode_storage:
        raise HTTPException(status_code=404, detail="Episode not found.")
    del episode_storage[episode_id]
    return {"status": "Episode deleted successfully."}


@app.post("/episodes/{episode_id}/generate_alternative", response_model=GenerationResponse)
async def generate_alternative(episode_id: UUID, request: GenerationRequest):
    """
    Generate an alternative title or description using an AI model.

    Args:
        episode_id: UUID of the episode to enhance.
        request: Contains the target field (title or description) and the prompt.

    Returns:
        A GenerationResponse object with the generated alternative.

    Raises:
        HTTPException 404 if episode not found.
    """
    episode = episode_storage.get(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found.")

    # Ukrainian instructions for the AI system prompt
    context = (
        f"Назва: {episode.title}\n"
        f"Опис: {episode.description}\n"
        f"Ведучий: {episode.host}"
    )

    alternative = await generate_alternative_text(
        context=context,
        instruction=request.prompt
    )

    return GenerationResponse(
        original_episode=episode,
        target=request.target,
        prompt=request.prompt,
        generated_alternative=alternative
    )
