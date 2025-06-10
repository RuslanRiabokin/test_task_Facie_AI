from typing import Dict
from uuid import UUID

from schemas import PodcastEpisode

# In-memory storage for podcast episodes.
# Key: UUID of the episode
# Value: PodcastEpisode object
episode_storage: Dict[UUID, PodcastEpisode] = {}
