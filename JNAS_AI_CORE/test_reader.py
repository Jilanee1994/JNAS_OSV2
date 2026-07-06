try:
    from JNAS_AI_CORE.tools.project_reader import ProjectReader
except ImportError:
    from tools.project_reader import ProjectReader

def main():
    reader = ProjectReader()

    project = reader.read_project()

    for file, code in project.items():

        print("=" * 60)
        print(file)
        print("=" * 60)

        print(code[:300])

        print()


if __name__ == "__main__":
    main()
