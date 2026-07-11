package build_agent

type BuildContext struct {
	Goal       string
	Plan       *Planner
	Executor   Executor
	Orchestrator Orchestrator
}

func NewBuildContext(goal string, plan *Planner, executor Executor, orchestrator Orchestrator) *BuildContext {
	return &BuildContext{
		Goal:       goal,
		Plan:       plan,
		Executor:   executor,
		Orchestrator: orchestrator,
	}
}
