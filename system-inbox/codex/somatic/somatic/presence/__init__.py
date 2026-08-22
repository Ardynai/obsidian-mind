"""Presence lane scaffold.

Presence and avatars are render-only and are never part of the reasoning path.
"""

from .avatar import PERSONAS, PresenceRender, render_presence

STATUS = "scaffolded"
RENDER_ONLY = True
REASONING_PATH_PARTICIPANT = False

__all__ = [
    "PERSONAS",
    "PresenceRender",
    "REASONING_PATH_PARTICIPANT",
    "RENDER_ONLY",
    "STATUS",
    "render_presence",
]
