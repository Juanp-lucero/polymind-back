
from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, decision: dict) -> dict:
        """
        Cada agente implementa su propio análisis.
        """
        pass

    def create_response(
        self,
        analysis: str,
        recommendations: list[str],
        observations: list[str] | None = None,
        alternative_evaluations: list[dict] | None = None
    ) -> dict:

        return {
            "agent": self.name,
            "analysis": analysis,
            "recommendations": recommendations,
            "observations": observations or [],
            "alternative_evaluations": alternative_evaluations or []
        }
