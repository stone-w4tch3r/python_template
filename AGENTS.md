# AI Guide - Python Project Template

**Authoritative reference for AI agents. Adherence to these standards is mandatory.**

---

## ⚡ Critical Reading Path

Before generating code, verify your context:

1.  **New Context?** → Review this document fully.
2.  **Implementation Phase?** → Consult [Coding Rules](docs/coding_rules.md) regarding the **Result Pattern**.

**Invariant Rule:** Run `uv run lint_full` continuously during generation cycles, not just at finalization.

---

## 🛠️ Toolchain & Environment

This project enforces a specific, modern stack. Do not deviate to older standards.

### Mandatory Components

*   **Runtime:** `Python 3.14+` (Leverage modern generic syntax and `TypeIs`).
*   **Dependency Manager:** `uv` (Used for all lifecycle tasks).
*   **Static Analysis:** `basedpyright` (Must run in **strict** mode).
*   **Linting/Formatting:** `ruff` (All-in-one).
*   **Core Library:** `rusty-results` (Enforces value-based error handling).

### Configuration Context (`pyproject.toml`)

```
# Key operational dependencies
dependencies = [
    "rusty-results",  # REQUIRED: See 'Error Handling Strategy'
]

# Development harness
dev = [
    "ruff",
    "basedpyright",   # Selected for speed + strictness over mypy
    "pytest",
    "pytest-cov",
]
```

---

## 📐 Development Standards

### 1. Error Handling Strategy (Strict Result Pattern)

**Directive:** Treat errors as return values, not control flow exceptions.

*   **Expected Failures (IO, Network, User Input):** MUST return `Result[T, E]`.
*   **Logic/Developer Errors (Invalid State):** MUST raise Exceptions (Fail-fast).
*   **Boundaries:** Catch 3rd-party exceptions immediately and wrap them in `Result`, also use global error boundaries.

**Implementation Example:**

```
from rusty_results import Result, Ok, Err

def retrieve_record(record_id: str) -> Result[Record, str]:
    """
    Retrieves a record safely.
    Returns Ok(Record) on success, Err(str) on expected IO failure.
    """
    path = resolve_path(record_id)

    # 1. Check expected failure condition
    if not path.exists():
        return Err(f"Record {record_id} is missing")

    try:
        # 2. Wrap boundary exceptions
        data = Record.parse(path)
        return Ok(data)
    except ValueError as e:
        return Err(f"Parse failure: {e}")

def _internal_consistency_check(value: int) -> None:
    # 3. Use exceptions ONLY for bugs (impossible states)
    if value < 0:
        raise ValueError("Internal logic error: negative value impossible here")
```

**Rationale:** This ensures type-safe error handling and prevents hidden control flow jumps.

### 2. Type System Requirements

*   **Mode:** Strict.
*   **Prohibitions:** No `Any`. No implicit types in public signatures.
*   **Data Structures:** Use `dataclasses` or `TypedDict`. Do not pass raw dictionaries.
*   **Routine:** Run `basedpyright src/` frequently to catch type drift early.

### 3. Rules For Async

**Rules**:
- **Always** `async` and `await` I/O operations (HTTP, files interaction, subprocess)
- **Never** do `subprocess.run()` or `time.sleep()` in main event loop of QT or other frameworks to avoid blocking
- To launch heavy async subprocess use `asyncio.create_subprocess_exec()` 
- For Qt use `qasync`
- Simple fast operations don't require async
---

## 🏗️ System Design

### Dependency Flow

The application follows a strict unidirectional dependency graph:

1.  **Presentation Layer (Top)**
    *   *Components:* Qt GUI or CLI (argparse) or API (FastAPI).
    *   *Role:* Consumer of Core. Handles input. Error catchers.
2.  **Domain Layer (Middle)**
    *   *Components:* Managers, Models, Business Rules.
    *   *Role:* Pure logic. Agnostic of UI.
3.  **Utility Layer (Bottom)**
    *   *Components:* Helpers, Common Utils.
    *   *Role:* Shared infrastructure.

---

## 🔄 Operational Workflow

Execute these commands via `uv` to maintain repository health.

| Goal | Command | Description |
| :--- | :--- | :--- |
| **Verify Code** | `uv run poe lint_full` | Runs formatting, linting, and strict type checking. |
| **Run Tests** | `uv run test` | Executes pytest suite. |
| **Launch** | `uv run app` | Starts the application. |
| **Pre-Commit** | `uv run lint_full && uv run test` | Mandatory check before finalizing task. |

---

**Ambiguity Resolution:**
If requirements are unclear, halt generation and request clarification from the human developer.
```
