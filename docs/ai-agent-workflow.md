# AI Agent Workflow

Recommended flow:

```text
Candidate repo
-> Testability Doctor
-> BountyLens if bounty issue
-> AI agent
-> AgentGate
-> Draft PR
-> Human review
```

## Practical Use

1. Run Testability Doctor on the candidate repository.
2. If the result is `good_for_agent`, pass the discovered test commands and risk flags to the agent.
3. If the result is `manual_setup_needed`, clarify setup and package boundaries first.
4. If the result is `docs_only`, keep work limited to docs unless tests are added.
5. If the result is `avoid`, keep the task with a human until validation can be made local and deterministic.

## Related Projects

- AgentGate: https://github.com/a78c7/agentgate
- BountyLens: https://github.com/a78c7/bountylens
