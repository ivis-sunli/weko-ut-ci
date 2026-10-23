"""Load a module configuration and build the Actions checkout matrix."""

import json
import re
import sys
from pathlib import Path

CONFIG_ROOT = Path(__file__).resolve().parents[1] / "config"


def load_modules(filename="modules.json"):
    path = (CONFIG_ROOT / filename).resolve()
    if not path.is_relative_to(CONFIG_ROOT) or path.suffix != ".json":
        raise ValueError("Choose a JSON file under config/, such as modules.json")
    entries = json.loads(path.read_text())
    if not isinstance(entries, list) or not entries:
        raise ValueError("The configuration must be a nonempty list of modules")

    modules = []
    names = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each module must be an object")
        for key in ("module", "repository", "branch"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError(f"Each module requires a nonempty {key}")
        module = entry["module"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", module) or module in names:
            raise ValueError(f"Invalid or duplicate module name: {module}")
        commit = entry.get("commit")
        if commit is not None and not isinstance(commit, str):
            raise ValueError(f"commit must be a string or null: {module}")
        commit = (commit or "").strip()
        modules.append(
            {
                "module": module,
                "repository": entry["repository"].strip(),
                "branch": entry["branch"].strip(),
                "commit": commit,
                "ref": commit or "refs/heads/" + entry["branch"].strip(),
            }
        )
        names.add(module)
    return modules


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "modules.json"
    print(json.dumps({"include": load_modules(filename)}))
