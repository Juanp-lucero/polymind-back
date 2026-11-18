
import os

import grpc

from app.grpc_service import decision_pb2
from app.grpc_service import decision_pb2_grpc


# "remote": conecta con el servidor gRPC (python -m app.grpc_service.grpc_server).
# "inprocess": ejecuta el servicio en el mismo proceso (necesario en Vercel,
# donde no se puede levantar un segundo servidor).
GRPC_MODE = os.getenv(
    "GRPC_MODE",
    "inprocess" if os.getenv("VERCEL") else "remote"
).strip().lower()
GRPC_SERVER_ADDRESS = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")


class InProcessRpcError(grpc.RpcError):

    def __init__(self, code, details):
        super().__init__(details)
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class _InProcessContext:

    def abort(self, code, details):
        raise InProcessRpcError(code, details)


def _call_analyzer(request):
    if GRPC_MODE == "inprocess":
        from app.grpc_service.grpc_server import DecisionAnalyzerService

        return DecisionAnalyzerService().AnalyzeDecision(
            request,
            _InProcessContext()
        )

    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        stub = decision_pb2_grpc.DecisionAnalyzerStub(channel)
        return stub.AnalyzeDecision(request, timeout=10)


def analyze_decision(
    decision_id: int,
    title: str,
    description: str,
    context: str,
    alternatives: list[str]
):
    request = decision_pb2.DecisionRequest(
        decision_id=decision_id,
        title=title,
        description=description,
        context=context or "",
        alternatives=alternatives
    )

    response = _call_analyzer(request)

    return {
        "decision_id": response.decision_id,
        "status": response.status,
        "analysis": response.analysis,
        "recommendations": list(response.recommendations),

        "agent_results": [
            {
                "agent": agent.agent,
                "analysis": agent.analysis,
                "recommendations": list(agent.recommendations),
                "observations": list(agent.observations),

                "alternative_evaluations": [
                    {
                        "alternative": evaluation.alternative,
                        "score": evaluation.score,
                        "justification": evaluation.justification
                    }
                    for evaluation in agent.alternative_evaluations
                ]
            }
            for agent in response.agent_results
        ],

        "alternative_comparison": [
            {
                "alternative": comparison.alternative,
                "criteria": dict(comparison.criteria),
                "weighted_score": comparison.weighted_score
            }
            for comparison in response.alternative_comparison
        ],

        "weights": dict(response.weights)
    }
