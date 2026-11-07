
from concurrent import futures

import grpc

from app.grpc_service import decision_pb2
from app.grpc_service import decision_pb2_grpc

from app.agents.orchestrator import Orchestrator


class DecisionAnalyzerService(
    decision_pb2_grpc.DecisionAnalyzerServicer
):

    def __init__(self):
        self.orchestrator = Orchestrator()

    def AnalyzeDecision(self, request, context):

        if not request.title.strip():
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Decision title is required"
            )

        if not request.description.strip():
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Decision description is required"
            )

        if not request.alternatives:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "At least one alternative is required"
            )

        decision = {
            "title": request.title,
            "description": request.description,
            "context": request.context,
            "alternatives": list(request.alternatives)
        }

        try:
            result = self.orchestrator.analyze_decision(decision)

            final_report = result["final_report"]

            response = decision_pb2.DecisionResponse(
                decision_id=request.decision_id,
                status=result["status"],
                analysis=final_report["analysis"],
                recommendations=final_report["recommendations"]
            )

            # Enviar los resultados individuales de cada agente
            for agent in result["agent_results"]:

                agent_message = response.agent_results.add(
                    agent=agent["agent"],
                    analysis=agent["analysis"]
                )

                agent_message.recommendations.extend(
                    agent.get("recommendations", [])
                )

                agent_message.observations.extend(
                    agent.get("observations", [])
                )

                for evaluation in agent.get(
                    "alternative_evaluations", []
                ):
                    agent_message.alternative_evaluations.add(
                        alternative=evaluation["alternative"],
                        score=evaluation["score"],
                        justification=evaluation["justification"]
                    )

            # Enviar la comparación ponderada
            for comparison in final_report.get(
                "alternative_evaluations", []
            ):

                comparison_message = (
                    response.alternative_comparison.add(
                        alternative=comparison["alternative"],
                        weighted_score=comparison["weighted_score"]
                    )
                )

                comparison_message.criteria.update(
                    comparison["criteria"]
                )

            # Enviar los pesos utilizados por el analista
            response.weights.update(
                self.orchestrator.analyst_agent.weights
            )

            return response

        except Exception as error:

            print(
                f"Error during multi-agent analysis: {error}"
            )

            context.abort(
                grpc.StatusCode.INTERNAL,
                "An error occurred during multi-agent analysis"
            )


def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    decision_pb2_grpc.add_DecisionAnalyzerServicer_to_server(
        DecisionAnalyzerService(),
        server
    )

    port = server.add_insecure_port("0.0.0.0:50051")

    if port == 0:
        raise RuntimeError(
            "Could not bind gRPC server to port 50051"
        )

    server.start()

    print(
        "Polymind IA Multi-Agent gRPC Server running on port 50051"
    )

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
