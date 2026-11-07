
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

            return decision_pb2.DecisionResponse(
                decision_id=request.decision_id,
                status=result["status"],
                analysis=final_report["analysis"],
                recommendations=final_report["recommendations"]
            )

        except Exception as error:
            print(f"Error during multi-agent analysis: {error}")

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
        raise RuntimeError("Could not bind gRPC server to port 50051")

    server.start()

    print("Polymind IA Multi-Agent gRPC Server running on port 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
