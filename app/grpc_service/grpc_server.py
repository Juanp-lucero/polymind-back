from concurrent import futures

import grpc

from app.grpc_service import decision_pb2
from app.grpc_service import decision_pb2_grpc


class DecisionAnalyzerService(
    decision_pb2_grpc.DecisionAnalyzerServicer
):

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

        analysis = (
            f"Decision received: {request.title}. "
            f"Description: {request.description}. "
            f"Context: {request.context}. "
            f"Number of alternatives: {len(request.alternatives)}."
        )

        recommendations = [
            f"Evaluate the advantages and disadvantages of: {alternative}"
            for alternative in request.alternatives
        ]

        return decision_pb2.DecisionResponse(
            decision_id=request.decision_id,
            status="analyzed",
            analysis=analysis,
            recommendations=recommendations
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    decision_pb2_grpc.add_DecisionAnalyzerServicer_to_server(
        DecisionAnalyzerService(),
        server
    )

    server.add_insecure_port("0.0.0.0:50051")

    server.start()

    print("Polymind IA gRPC Server running on port 50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
