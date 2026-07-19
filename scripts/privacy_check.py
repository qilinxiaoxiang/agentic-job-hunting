from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
DENY = [
    "/" + "Users/",
    "@" + "andrew.cmu.edu",
    "shawn" + ".xiang",
    "Open" + "Assets",
    "BEGIN " + "PRIVATE KEY",
    "ghp" + "_",
]


def main() -> int:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.resolve() == SELF or ".git" in path.parts:
            continue
        if any(part in {".venv", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(token in text for token in DENY):
            failures.append(str(path.relative_to(ROOT)))
    if failures:
        print("private token found in: " + ", ".join(failures))
        return 1
    print("privacy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
