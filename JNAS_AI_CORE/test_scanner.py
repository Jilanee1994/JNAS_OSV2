try:
    from JNAS_AI_CORE.tools.project_scanner import ProjectScanner
except ImportError:
    from tools.project_scanner import ProjectScanner

def main():
    scanner = ProjectScanner()

    files = scanner.scan()

    print("=" * 60)

    for file in files:
        print(file["path"])


if __name__ == "__main__":
    main()
