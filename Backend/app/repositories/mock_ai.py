from app.models.entities import AiInsight, AiScan
from app.repositories.base import AiInsightRepository, AiScanRepository, InMemoryRepository


class MockAiScanRepository(InMemoryRepository[AiScan], AiScanRepository):
    def __init__(self):
        super().__init__(AiScan, [], id_prefix="SCAN-")


class MockAiInsightRepository(InMemoryRepository[AiInsight], AiInsightRepository):
    def __init__(self):
        super().__init__(AiInsight, [], id_prefix="INS-")
