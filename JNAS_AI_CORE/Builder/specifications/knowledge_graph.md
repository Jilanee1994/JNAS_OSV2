# KNOWLEDGE_GRAPH Specification

IMPORTANT

Do NOT generate a Hello application.

Do NOT generate greet().

Do NOT generate --name.

Do NOT generate placeholder code.

Do NOT generate NotImplementedError.

Return ONLY valid Python code.

## Goal

Build a Knowledge Graph engine for JNAS AI Core.

The project manages entities and relationships inside an enterprise knowledge graph.

Language: Python

Project Structure

README.md
requirements.txt

src/
    __init__.py
    main.py
    graph.py
    entity.py
    relationship.py

tests/
    test_main.py

Required Classes

KnowledgeGraph
Entity
Relationship

Required Functions

add_entity()
remove_entity()
add_relationship()
find_entity()
find_relationships()
main(argv=None)

CLI

python main.py --entity Robot

Tests MUST import

from src.main import (
    KnowledgeGraph,
    Entity,
    Relationship,
)

Requirements

- Store entities
- Store relationships
- Search entities
- Search relationships
- Prevent duplicate entities
- Prevent duplicate relationships
- Export graph summary
- Command-line interface
- Complete unit tests

Never

- Hello application
- TODO
- FIXME
- XXX
- Placeholder comments
- Replace with actual...
- Example implementation
- Dummy implementation
- NotImplementedError
- pass statements
- Markdown
- Code fences
- Java
- Go
- Rust
- JavaScript
- TypeScript
- PHP
- Swift

The implementation and tests MUST use the same API.

Return production-quality Python code only.
