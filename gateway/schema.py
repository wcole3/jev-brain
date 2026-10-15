"""The Jev /v1/systemone request (TypeSafe wire format) and the refusal error."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

MAX_OPTIONS = 255
MAX_LEVELS = 10


class RequestError(ValueError):
    """Refused with HTTP 422. Capacity messages keep the decision-index harness marker text."""


class ImageError(RequestError):
    """A bad image, too many images or an oversized body: refused with HTTP 400, not 422."""


class Question(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["choice", "score", "noul"]
    instructions: Any = None
    criteria: Any = None


class SystemOneRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state: Any = ""
    model: str = "jev-latest"
    questions: dict[str, Question]
    layout: str | None = None  # experiment override, not part of Jev's API
    option_orders: str | None = None  # experiment override, not part of Jev's API
    images: list[str] | None = None  # data: URLs or base64, shown before the state
