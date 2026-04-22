from agent_pr_reviewer.runtime.retry import RetryPolicy, RetryableToolError


def test_retry_policy_retries_until_success() -> None:
    attempts = {"count": 0}

    def flaky_operation() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RetryableToolError("temporary failure")
        return "ok"

    policy = RetryPolicy(attempts=3, backoff_seconds=0)
    result = policy.run(flaky_operation)

    assert result == "ok"
    assert attempts["count"] == 3
