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
            context=context,
            alternatives=alternatives
        )

        response = stub.AnalyzeDecision(
            request,
            timeout=10
        )

        return response


if __name__ == "__main__":

    result = analyze_decision(
        decision_id=1,
        title="Implementar una tienda virtual",
        description="Evaluar el desarrollo de una plataforma de comercio electrónico.",
        context="Una empresa quiere ampliar sus ventas mediante internet.",
        alternatives=[
            "Desarrollar una plataforma propia",
            "Contratar una plataforma comercial",
            "Utilizar una solución de código abierto"
        ]
    )

    print("\n===== POLYMIND IA - RESPUESTA gRPC =====")
    print("ID de decisión:", result.decision_id)
    print("Estado:", result.status)
    print("Análisis:", result.analysis)
    print("Recomendaciones:")

    for recommendation in result.recommendations:
        print("-", recommendation)