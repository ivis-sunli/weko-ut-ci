"""Combine each module's result and keep all raw reports beside the index."""

import csv
import html
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from module_config import load_modules

root = Path("reports")
root.mkdir(exist_ok=True)
rows = []
filename = sys.argv[1] if len(sys.argv) > 1 else "modules.json"
for entry in load_modules(filename):
    module = entry["module"]
    folder = root / "raw" / ("module-" + module)
    row = {
        "module": module,
        "status": "incomplete",
        "tests": "",
        "failures": "",
        "errors": "",
        "skipped": "",
    }
    exit_code = folder / "exit-code.txt"
    junit = folder / "junit.xml"
    if exit_code.exists() and junit.exists():
        try:
            document = ET.parse(junit).getroot()
            suites = (
                [document]
                if document.tag == "testsuite"
                else list(document.iter("testsuite"))
            )
            for key in ("tests", "failures", "errors", "skipped"):
                row[key] = sum(int(suite.get(key, 0)) for suite in suites)
            row["status"] = (
                "passed"
                if exit_code.read_text().strip() == "0"
                and not (row["failures"] or row["errors"])
                and row["tests"]
                else "failed"
            )
        except (ET.ParseError, ValueError):
            row["status"] = "incomplete"
    elif exit_code.exists() and exit_code.read_text().strip() != "0":
        row["status"] = "failed"
    rows.append(row)

with (root / "summary.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
headers = "".join(f"<th>{key}</th>" for key in rows[0])
body = []
for row in rows:
    module = row["module"]
    link = f'<a href="raw/module-{module}/run.log">{module}</a>'
    body.append(
        "<tr><td>"
        + link
        + "</td>"
        + "".join(
            f"<td>{html.escape(str(value))}</td>"
            for key, value in row.items()
            if key != "module"
        )
        + "</tr>"
    )
(root / "index.html").write_text(
    '<!doctype html><meta charset="utf-8"><title>WEKO unit tests</title>'
    "<h1>WEKO unit tests</h1><p>Raw logs, JUnit and coverage reports are in each module folder.</p>"
    '<table border="1"><thead><tr>'
    + headers
    + "</tr></thead><tbody>"
    + "".join(body)
    + "</tbody></table>"
)
