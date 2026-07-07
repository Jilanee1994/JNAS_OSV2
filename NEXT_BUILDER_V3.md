# Builder Agent V3 Deferred Improvements

- Add richer provider-specific request/response adapters for Gemini, Groq, and OpenRouter chat completion payload formats.
- Add build session persistence so long V2 builds can resume after process restart.
- Add per-file dependency ordering informed by Planner task output.
- Add sandboxed generated-project execution for tests that require runtime side effects.
- Add coverage measurement for generated projects.
- Add optional human approval gates for protected paths.
- Add registry registration so Builder V2 can be resolved as a Tool Registry worker.
