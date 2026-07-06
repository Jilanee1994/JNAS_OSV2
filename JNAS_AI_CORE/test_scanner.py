from tools.project_scanner import ProjectScanner

scanner = ProjectScanner()

files = scanner.scan()

print("=" * 60)

for file in files:
    print(file["path"])
