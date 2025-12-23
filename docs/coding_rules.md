# Code Standards Guide

**Quality rules for Python code. Mandatory compliance.**

---

## Type System Rules

### Enforcement

Run type checks constantly during work, not just at the end:

```
uv run poe lint_full
# Must show: 0 errors
```

### Configuration

```
[tool.basedpyright]
pythonVersion = "3.14"
typeCheckingMode = "strict"
reportAny = "error"
```

**Non-negotiable**: Strict mode + zero `Any` types. Treat `Unknown` and `Any` as bugs to fix, not suppress.

### Required Patterns

**Type everything**:
```
# ✅ Correct
def build_item(name: str, ver: str) -> Item:
    ...

# ❌ Wrong
def build_item(name, ver):
    ...
```

**No vague types**:
```
# ✅ Correct
def parse_config(cfg: dict[str, str | int]) -> None:
    ...

# ❌ Wrong
def parse_config(cfg: Any) -> None:
    ...
```

**Ban raw dictionaries for app data**:
- Never pass untyped `dict[str, object]` between functions
- Use TypedDict for JSON/config shapes
- Use dataclasses for domain objects
- Validate external input immediately into typed structures

**Prefer Result over optional**:
```
# ✅ Correct
def fetch_item(id: str) -> Result[Item, str]:
    if not exists(id):
        return Err("not found")
    return Ok(load(id))

# ❌ Wrong
def fetch_item(id: str) -> Item | None:
    if not exists(id):
        return None
    return load(id)
```

**Use modern Python 3.14 features**:
```
from typing import TypedDict, Required, NotRequired, TypeIs

class Config(TypedDict):
    name: Required[str]
    url: NotRequired[str]

def is_loaded(obj: object) -> TypeIs[Item]:
    return isinstance(obj, Item) and obj.ready
```

**Document complex types**:
```
Settings = dict[str, str | int | bool | None]

def apply_settings(s: Settings) -> None:
    ...
```

### Type Patterns

**TypedDict** (for JSON/config):
```
class UserData(TypedDict):
    id: str
    active: bool
```

**Dataclass** (for domain objects):
```
from dataclasses import dataclass

@dataclass
class Item:
    id: str
    name: str
    active: bool = True
```

**Protocol** (for interfaces):
```
from typing import Protocol

class Storage(Protocol):
    def save(self, data: bytes) -> None: ...
```

**TypeAlias** (for readability):
```
from typing import TypeAlias

Config: TypeAlias = dict[str, str | bool]
```

### Handling Any/Unknown

**Default rule**: `Unknown` and `Any` are defects. Fix the source, don't suppress.

**At library boundaries**, convert immediately:
```
raw = json.loads(text)
if not isinstance(raw, dict):
    return Err("expected object")
data = cast(dict[str, object], raw)
cfg = Config.from_dict(data)
```

**For third-party APIs without types**, use `cast` narrowly and document why.

---

## Code Style

### Tool Configuration

```
uv run poe lint_full  # Format + lint
```

```
[tool.ruff]
line-length = 130
target-version = "py314"

select = [
    "E", "F", "I", "N", "W", "UP", "ASYNC",
    "S", "B", "A", "C4", "RUF"
]

ignore = ["S101"]  # Allow assert in tests

[tool.ruff.per-file-ignores]
"tests/**/*.py" = ["S101"]
```

### Naming

| Item | Style | Example |
|------|-------|---------|
| Module | `snake_case` | `item_store.py` |
| Class | `PascalCase` | `ItemStore` |
| Function | `snake_case` | `load_item()` |
| Variable | `snake_case` | `item_id` |
| Constant | `UPPER_SNAKE` | `MAX_SIZE` |
| Private | `_prefix` | `_internal()` |

**Constants location**: Define in `src/app/config.py`, import from there.

### Import Order

Ruff auto-sorts, but expect:
```
# Standard library
import sys
from pathlib import Path

# Third-party
import httpx

# Local
from app.core.item import Item
```

### String Quotes

Use double quotes:
```
# ✅ Correct
name = "Item"

# ❌ Wrong
name = 'Item'
```

Exception: Avoid escaping in nested quotes:
```
msg = 'Said "hello"'  # OK
```

---

## Async Rules

### When to Use

**Use async for**:
- I/O operations (file, network, subprocess)
- Operations taking >100ms
- Concurrent operations

**Don't use async for**:
- Data transformations
- Pure functions
- Non-blocking code

### Implementation

**Never block the loop**:
```
# ❌ Wrong
def run_tool(item: Item) -> int:
    result = subprocess.run(["tool", ...])  # Blocks!
    return result.returncode

# ✅ Correct
async def run_tool(item: Item) -> int:
    proc = await asyncio.create_subprocess_exec("tool", ...)
    return await proc.wait()
```

**Use async context managers**:
```
async with httpx.AsyncClient() as client:
    resp = await client.get(url)
```

**Run operations concurrently**:
```
# ✅ Correct
files = await asyncio.gather(
    download(url1),
    download(url2),
    download(url3)
)

# ❌ Wrong
f1 = await download(url1)
f2 = await download(url2)
f3 = await download(url3)
```

**Handle timeouts**:
```
async def fetch(url: str) -> bytes:
    try:
        async with asyncio.timeout(30):
            return await download(url)
    except asyncio.TimeoutError:
        logger.error(f"Timeout: {url}")
        raise
```

**Don't mix sync/async**:
```
# ❌ Wrong
def sync_wrapper(url: str) -> bytes:
    return asyncio.run(fetch_async(url))  # New loop!

# ✅ Correct
async def fetch(url: str) -> bytes:
    ...
```

---

## Error Handling

### Philosophy

**Errors are values, not control flow.**

Use Result pattern for expected failures. Use exceptions only for bugs.

### Result Library

```
from rusty_results import Result, Ok, Err

def load_item(id: str) -> Result[Item, str]:
    """Load item by ID.
    
    Returns:
        Ok(Item) on success
        Err(message) on expected failure
    """
    path = get_path(id)
    
    if not path.exists():
        return Err(f"Item {id} not found")
    
    try:
        data = json.loads(path.read_text())
        item = Item.from_dict(data)
        return Ok(item)
    except json.JSONDecodeError as e:
        return Err(f"Corrupted: {e}")
    except KeyError as e:
        return Err(f"Missing field: {e}")
```

**Dependencies**:
```
dependencies = ["rusty-results"]
```

### When to Use Each

**Result for** (default):
- Expected failures (user input errors, file not found, network issues)
- Library functions callers will handle
- Normal operation failures
- Chainable operations

**Exception for** (fail-fast):
- Programming errors (assertions, invalid state)
- Unexpected conditions (out of memory, disk full)
- Invariant violations (should never happen)
- Unrecoverable errors

**Examples**:
```
# ✅ Result: Expected failure
def create_item(name: str) -> Result[Item, str]:
    if exists(name):
        return Err(f"Item {name} exists")
    return Ok(Item(name=name))

# ✅ Exception: Programming error
def _validate_path(path: Path) -> None:
    if not is_safe(path):
        raise SecurityError(f"Unsafe: {path}")  # Bug!
```

### Early Returns

Handle errors with early returns:

```
async def start_item(id: str) -> Result[int, str]:
    """Start item process.
    
    Returns:
        Ok(pid) on success
        Err(message) on failure
    """
    item_result = load_item(id)
    if item_result.is_err():
        return Err(f"Cannot start: {item_result.unwrap_err()}")
    
    item = item_result.unwrap()
    
    if item.pid and psutil.pid_exists(item.pid):
        return Err(f"Already running: {item.pid}")
    
    try:
        proc = await asyncio.create_subprocess_exec(...)
        return Ok(proc.pid)
    except OSError as e:
        return Err(f"Start failed: {e}")
```

### Error Boundaries

**Convert library exceptions to Results**:
```
def load_json(path: Path) -> Result[dict, str]:
    try:
        data = json.loads(path.read_text())
        return Ok(data)
    except FileNotFoundError:
        return Err(f"Not found: {path}")
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON: {e}")
    except PermissionError:
        return Err(f"Access denied: {path}")
    except Exception as e:
        logger.error(f"Unexpected: {path}", exc_info=True)
        return Err(f"Unexpected: {e}")
```

**UI error boundaries**:
```
class Window:
    async def on_start_clicked(self):
        id = self.get_selected()
        
        try:
            result = await start_item(id)
            
            if result.is_ok():
                pid = result.unwrap()
                self.show_success(f"Started: {pid}")
            else:
                err = result.unwrap_err()
                self.show_error(f"Failed: {err}")
        
        except Exception as e:
            logger.error("Unexpected", exc_info=True)
            self.show_error(f"Error: {e}")
```

**Global error boundary**:
```
def main():
    try:
        app = setup()
        run(app)
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as e:
        logger.critical("Crashed", exc_info=True)
        show_error_dialog(f"Crash: {e}")
        sys.exit(1)
```

### Result Helpers

```
# Unwrap with default
item = load_item(id).unwrap_or(default)

# Map over Result
name = load_item(id).map(lambda i: i.name)

# Chain operations
def get_url(id: str) -> Result[str | None, str]:
    return load_item(id).map(lambda i: i.url)

# Convert to exception (at boundaries only)
try:
    item = load_item(id).unwrap()
except Exception as e:
    handle(e)
```

### Custom Errors

For complex errors, use dataclasses:
```
@dataclass
class FetchError:
    url: str
    code: int | None
    msg: str

async def fetch(url: str) -> Result[Path, FetchError]:
    try:
        resp = await httpx.get(url)
        resp.raise_for_status()
        return Ok(save(resp))
    except httpx.HTTPStatusError as e:
        return Err(FetchError(
            url=url,
            code=e.response.status_code,
            msg=f"HTTP {e.response.status_code}"
        ))
    except httpx.NetworkError as e:
        return Err(FetchError(
            url=url,
            code=None,
            msg=f"Network: {e}"
        ))
```

### Logging with Results

```
result = load_item(id)
if result.is_err():
    logger.error(f"Load failed '{id}': {result.unwrap_err()}")
    return result
```

### Exception Hierarchy

Define exceptions for programming errors:
```
class AppError(Exception):
    """Base for programming errors."""

class InvalidStateError(AppError):
    """Invalid state (should never happen)."""
```

### Summary

1. Default to Result for operations that can fail normally
2. Use exceptions only for programming errors (fail-fast)
3. Convert library exceptions to Results at boundaries
4. Use early returns for clean Result handling
5. Add error boundaries in UI components
6. Use descriptive error messages or custom error types
7. Propagate Results through call chain
8. Log failures but don't crash
9. Handle async cancellation properly

---

## Documentation

### Docstrings

Use Google-style for public APIs:
```
def create_item(name: str, ver: str, url: str | None = None) -> Item:
    """Create new item.
    
    Args:
        name: Item name (unique)
        ver: Version (e.g., "1.0.0")
        url: Optional URL
    
    Returns:
        Created Item
    
    Raises:
        ItemExistsError: Name already used
        ValueError: Invalid URL
    
    Example:
        >>> mgr = Manager()
        >>> item = mgr.create_item("Test", "1.0.0")
        >>> print(item.name)
        Test
    """
    ...
```

For simple functions, one line is fine:
```
def is_active(item: Item) -> bool:
    """Check if item is active."""
    return item.active
```

### Generated Docs

Generated docs must be deterministic:
- No timestamps
- No run-dependent ordering
- Sort inputs before rendering
- Repeated runs without code changes produce identical output

### Comments

Write self-documenting code. Use comments sparingly.

```
# ✅ Correct: Explains "why"
# Absolute paths required for subprocess
workdir = str(item.path.resolve())

# ❌ Wrong: Repeats code
# Set workdir to path
workdir = str(item.path.resolve())
```

**When to comment**:
- Complex algorithms
- Non-obvious workarounds
- TODO/FIXME markers
- Security-critical code

```
# TODO: Add better isolation
# SECURITY: Must validate no symlinks
if not is_safe(path, base):
    raise SecurityError("Symlink detected")
```

---

## Security

### Path Validation

Always validate paths:
```
from app.utils.paths import is_safe_path, get_data_dir

def load_item(id: str) -> Item:
    path = get_data_dir() / "items" / id
    
    # SECURITY: Check symlinks
    if not is_safe_path(path, get_data_dir() / "items"):
        raise SecurityError(f"Unsafe path: {path}")
    
    return Item.from_file(path / "item.json")
```

### Input Validation

Validate all user input:
```
def validate_name(name: str) -> None:
    """Validate name is filesystem-safe.
    
    Raises:
        ValueError: Invalid name
    """
    if not name:
        raise ValueError("Name required")
    
    if len(name) > 255:
        raise ValueError("Name too long")
    
    if "/" in name or "\\" in name:
        raise ValueError("No path separators")
    
    if name in (".", "..", "CON", "PRN", "AUX", "NUL"):
        raise ValueError(f"Reserved name: {name}")
```

### Subprocess Safety

Never use `shell=True`:
```
# ✅ Correct
await asyncio.create_subprocess_exec("tool", "-in", path)

# ❌ Wrong: Injection risk!
await asyncio.create_subprocess_shell(f"tool -in {path}")
```

Validate command arguments:
```
# ✅ Correct
binary = get_binary(ver)
if not binary.exists():
    raise FileNotFoundError(f"Binary not found: {binary}")

await asyncio.create_subprocess_exec(str(binary), ...)
```

---

## Performance

### Guidelines

1. Write clear code first, optimize later
2. Profile before optimizing
3. Optimize hot paths first
4. Use appropriate data structures

### Recommendations

**Use `__slots__` for frequent objects** (measure first):
```
@dataclass(slots=True)
class Item:
    id: str
    name: str
```

**Batch operations**:
```
# ✅ Correct
save_all(items)

# ❌ Wrong
for item in items:
    save(item)
```

**Lazy loading**:
```
class Item:
    def __init__(self, ...):
        self._size: int | None = None
    
    @property
    def size(self) -> int:
        if self._size is None:
            self._size = calc_size(self.path)
        return self._size
```

**Concurrent I/O**:
```
# ✅ Correct
results = await asyncio.gather(*[call(url) for url in urls])
```

---

## Git Commits

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructure
- `perf`: Performance
- `test`: Tests
- `chore`: Build/dependencies

### Examples

```
feat(core): add item export

- Add export_item() to Manager
- Create ZIP format
- Add tests

Closes #42
```

```
fix(ui): prevent crash on stop

Check item.pid before calling psutil.

Fixes #56
```

```
docs(readme): update for Python 3.14
```

---

## Review Checklist

Before requesting review:

- [ ] `uv run poe lint_full` passes
- [ ] `uv run poe test` passes
- [ ] New code has tests
- [ ] Public APIs have docstrings
- [ ] Security considerations addressed
- [ ] No hardcoded secrets
- [ ] Error messages are clear
- [ ] Commit messages follow convention
- [ ] No debug code or eexcessive comments
