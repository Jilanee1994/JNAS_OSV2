from tools.project_reader import ProjectReader

reader = ProjectReader()

project = reader.read_project()

for file, code in project.items():

    print("=" * 60)
    print(file)
    print("=" * 60)

    print(code[:300])

    print() 
