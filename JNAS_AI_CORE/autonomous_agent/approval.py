from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    task: str
    plan: object
    approved: bool = False


class ApprovalGate:

    def create_request(self, task: str, plan: object) -> ApprovalRequest:
        return ApprovalRequest(
            task=task,
            plan=plan
        )

    def show(self, request: ApprovalRequest) -> None:
        print("\n" + "=" * 50)
        print("JNAS CHANGE APPROVAL REQUEST")
        print("=" * 50)

        print("Task:")
        print(request.task)

        print("\nPlan:")
        print(request.plan)

        print("\nStatus:")
        print("WAITING FOR APPROVAL")

        print("=" * 50)

    def approve(self, request: ApprovalRequest) -> None:
        request.approved = True

    def reject(self, request: ApprovalRequest) -> None:
        request.approved = False
