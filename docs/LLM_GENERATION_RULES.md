# LLM GENERATION RULES

Every generated project MUST satisfy these rules.

1. Return ONLY ===FILE:path=== blocks.

2. Never return markdown.

3. Never use ``` or code fences.

4. Never generate Hello application unless project == HELLO.

5. Never generate TODO, FIXME, XXX.

6. Never generate NotImplementedError.

7. Never generate placeholder comments.

8. Never generate:
   - Replace with actual...
   - Example implementation...
   - Dummy implementation...

9. Never import undeclared dependencies.

10. Every imported package must exist in requirements.txt.

11. Every symbol imported by tests MUST exist.

12. Every generated class MUST be implemented.

13. Every generated function MUST contain working logic.

14. Never generate duplicate functions.

15. Never generate duplicate classes.

16. Never generate broken file headers.

17. Always return one final ===END===.

18. The implementation and tests must use the same API.

19. Never invent different function names between implementation and tests.

20. Generate production-quality code only.
