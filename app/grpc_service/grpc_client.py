
import grpc

from app.grpc_service import decision_pb2
from app.grpc_service import decision_pb2_grpc


def analyze_decision(
    decision_id: int,
    title: str,
    description: str,
    context: str,
    alternatives: list[str]
):
    with grpc.insecure_channel("localhost:50051") as channel:

        stub = decision_pb2_grpc.DecisionAnalyzerStub(channel)

        request = decision_pb2.DecisionRequest(
            decision_id=decision_id,
            title=title,
            description=description,
            context=context or "",
            alternatives=alternatives
        )

        response = stub.AnalyzeDecision(request, timeout=10)

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
