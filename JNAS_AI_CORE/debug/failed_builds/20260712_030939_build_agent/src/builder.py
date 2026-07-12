class BuilderStepExecutor:
    def execute_step(self, step: dict) -> dict:
        result = {
            "status": "completed",
            "message": f"Executed {step['name']} successfully."
        }
        # Simulate a failed execution
        if step["name"] == "failed_step":
            result["status"] = "failed"
            result["message"] += " but failed."

        return result
