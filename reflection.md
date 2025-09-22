# Reflection: AI’s Impact on Building the Online Library

AI meaningfully accelerated the development of this project by reducing the time spent on boilerplate and helping enforce consistent patterns. The most impactful use case was scaffolding: given the endpoint plan and the folder structure, in-IDE AI helped rapidly create routers, schemas, and service stubs that matched FastAPI best practices. This freed up attention for higher‑value work like refining validation, tightening guard clauses, and improving error semantics.

Prompting strategies mattered. The best results came from providing a compact but rich context: project goals, minimal API spec, data models, and the existing file tree. Using Receive an Object, Return an Object (RORO) conventions and explicit type hints encouraged AI to generate code aligned with the codebase’s style. Short, iterative prompts outperformed long monologues. I learned to request focused edits (“add early returns for invalid states,” “convert to lifespan context manager”) and to keep the scope of each prompt narrow.

AI-assisted code reviews were also valuable. Before committing, I asked the assistant to look for missing guard clauses, ambiguous exception handling, and potential blocking calls. This led to standardizing error responses, converting startup events to a lifespan context manager, and clarifying function names. The review pass occasionally over-suggested abstractions; human judgment was needed to keep the code direct and readable.

Testing benefited from AI as well. It generated initial integration test templates for authentication and book management, which I then adapted to local fixtures and edge cases. The assistant helped identify boundary conditions worth asserting, such as invalid tokens, missing permissions, and nonexistent records.

Documentation and developer experience improved through AI-suggested edits. The README now calls out the `src/` layout and `PYTHONPATH` export, and includes explicit instructions for running, testing, and formatting. AI also helped refine docstrings toward concise purpose statements with explicit return types.

What felt limiting: AI sometimes hallucinated module paths or proposed unnecessary abstractions. It also needs precise context to avoid mismatched names across routers, schemas, and services. To mitigate this, I validated imports immediately, searched the codebase for usage consistency, and insisted on concrete, minimal changes in each iteration.

Key lessons about prompting, reviewing, and iterating:

- Be specific about inputs/outputs and file locations; reference exact modules (e.g., `app/routers/books.py`).
- Prefer many small prompts over one large prompt. Each should have a single outcome.
- Ask for alternatives sparingly; choose one, then iterate with diffs.
- Run tests early and often; use failures to drive the next prompt.
- Keep humans in the loop for design choices and performance trade-offs.

Overall, AI acted as a fast pair programmer that excels at repetition and pattern propagation while I focused on correctness, performance, and clarity. The combination yielded a cleaner, more consistent FastAPI codebase delivered in less time.


