from app.mock_data.approvals import APPROVALS
from app.models.entities import Approval
from app.models.enums import ApprovalStatus
from app.repositories.base import ApprovalRepository, InMemoryRepository


class MockApprovalRepository(InMemoryRepository[Approval], ApprovalRepository):
    def __init__(self):
        super().__init__(Approval, APPROVALS, id_prefix="APR-")

    def get_pending_for_purchase_order(self, purchase_order_id: str) -> Approval | None:
        for approval in self.list():
            if approval.purchase_order_id == purchase_order_id and approval.status == ApprovalStatus.PENDING:
                return approval
        return None
