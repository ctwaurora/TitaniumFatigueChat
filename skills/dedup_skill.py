import hashlib
import json
from pathlib import Path


PAPER_INDEX_PATH = Path("data/paper_index.json")


def compute_file_hash(file_path: str) -> str:
    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(block)

    return sha.hexdigest()


def _load_index() -> list:
    if not PAPER_INDEX_PATH.exists():
        return []

    try:
        return json.loads(PAPER_INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def check_duplicate(file_hash: str) -> bool:
    index = _load_index()
    return any(item.get("file_hash") == file_hash for item in index)


def add_to_index(file_hash: str, file_name: str, saved_path: str) -> None:
    PAPER_INDEX_PATH.parent.mkdir(exist_ok=True)
    index = _load_index()

    if any(item.get("file_hash") == file_hash for item in index):
        return

    index.append(
        {
            "file_hash": file_hash,
            "file_name": file_name,
            "saved_path": saved_path,
            "card_generated": True,
        }
    )

    PAPER_INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )