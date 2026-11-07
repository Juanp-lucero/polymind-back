
from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, decision: dict) -> dict:
        """
        Cada agente debe implementar
        su propio proceso de análisis.
        """
        pass

    def create_response(
        self,
        analysis: str,
        recommendations: list[str],
        observations: list[str] | None = None
    ) -> dict:

        return {
            "agent": self.name,
            "analysis": analysis,
            "recommendations": recommendations,
            "observations": observations or []
        }
