"""Definition of pydantic models."""

from pydantic import BaseModel


class Car(BaseModel):  # type: ignore
    """Representation of a car send by the API."""

    name: str
    description: str
    distance: float
