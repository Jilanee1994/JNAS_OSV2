package build_agent

type Step struct {
	name string
}

func NewStep(name string) *Step {
	return &Step{
		name: name,
	}
}

func (s *Step) Execute() error {
	log.Printf("Executing step %s", s.name)
	return nil
}

func (s *Step) Retry() {
	log.Printf("Retrying step %s", s.name)
}
