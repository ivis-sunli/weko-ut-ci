"""Allow the legacy c1 dependencies to build on Python 3.12."""

import subprocess
import sys

args = sys.argv[1:]
# tox-setuptools-version first installs the module's legacy setuptools version.
# Restore the compatible build tools before installing requirements2.txt.
if any(arg.startswith("-r") for arg in args):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "setuptools==71.0.3",
            "wheel==0.45.1",
            "pytest-runner==4.5.1",
            "setuptools-scm==8.3.1",
            "Babel==2.14.0",
            "xmlschema==1.0.8",
            "elementpath==1.1.2",
        ],
        check=True,
    )
raise SystemExit(
    subprocess.call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-build-isolation",
            *args,
        ]
    )
)
