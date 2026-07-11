package build_agent

import (
	"fmt"
	"log"
	"os"
)

type Executor interface {
	ExecuteStep(step Step) error
}

type Orchestrator struct {
	Queue *TaskQueue
}

type Planner struct {
	Tasks []Task
}

type TaskQueue struct {
	tasks []Task
}

type Task struct {
	Name    string
	Builder func(*BuildContext) error
}

type BuildContext struct {
	Goal       string
	Plan       *Planner
	Executor   Executor
	Orchestrator Orchestrator
}

type Step interface {
	Execute() error
	Retry()
}

func NewBuildContext(goal string, plan *Planner, executor Executor, orchestrator Orchestrator) *BuildContext {
	return &BuildContext{
		Goal:       goal,
		Plan:       plan,
		Executor:   executor,
		Orchestrator: orchestrator,
	}
}

type CommandInterface struct {
}

func (c *CommandInterface) Run() error {
	fmt.Println("Running build agent command interface")
	return nil
}
