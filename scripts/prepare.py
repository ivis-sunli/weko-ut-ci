"""Prepare the disposable source checkout, then its installed c1 runtime."""

import base64
import json
import os
import secrets
import ssl
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def checkout(module, source):
    env = {}
    for name in ("Dockerfile", "opensearch/Dockerfile"):
        for line in (source / name).read_text().splitlines():
            if line.startswith("ENV ") and "=" in line:
                key, value = line[4:].split("=", 1)
                if (
                    key not in ("PATH", "VIRTUALENVWRAPPER_PYTHON")
                    and "${" not in value
                ):
                    env[key] = value.strip().strip('"')
    db_password = secrets.token_hex(16)
    rabbit_password = secrets.token_hex(16)
    env.update(
        {
            "MODULE": module,
            "WEKO_SOURCE": str(source),
            "CI_DB_PASSWORD": db_password,
            "CI_RABBIT_PASSWORD": rabbit_password,
            "CI_SEARCH_ADMIN_PASSWORD": secrets.token_hex(16) + "Aa9!",
            "INVENIO_POSTGRESQL_DBPASS": db_password,
            "SQLALCHEMY_DATABASE_URI": f"postgresql+psycopg2://invenio:{db_password}@postgresql/invenio",
            "INVENIO_RABBITMQ_USER": "ci",
            "INVENIO_RABBITMQ_PASS": rabbit_password,
            "QUEUES_TEST_VHOST": "queues_ut_ci",
            "BROKER_URL": f"amqp://ci:{rabbit_password}@rabbitmq:5672//",
            "QUEUES_BROKER_URL": f"amqp://ci:{rabbit_password}@rabbitmq:5672//",
            "CACHE_REDIS_HOST": "redis",
            "CACHE_REDIS_URL": "redis://redis:6379/0",
            "ACCOUNTS_SESSION_REDIS_URL": "redis://redis:6379/1",
            "SEARCH_HOST": "opensearch",
            "SEARCH_OPENSEARCH_HOSTS": "opensearch",
            "LANG": "C.UTF-8",
            "USER": "invenio",
            "INVENIO_ROLE_SYSTEM": "System Administrator",
            "INVENIO_ROLE_REPOSITORY": "Repository Administrator",
            "INVENIO_ROLE_COMMUNITY": "Community Administrator",
            "CI_ARTIFACT_DIR": "/reports",
            "COVERAGE_FILE": "/reports/.coverage",
            "EVIDENCE_PREFIX": "/reports/evidence",
        }
    )
    for key, value in env.items():
        if os.getenv("GITHUB_ACTIONS") == "true" and ("PASS" in key or "SECRET" in key):
            print("::add-mask::" + value, flush=True)
    Path(".env").write_text("".join(f"{k}={v}\n" for k, v in env.items()))
    Path(".env").chmod(0o600)
    cfg = source / "scripts/instance.cfg"
    cfg.write_text(
        cfg.read_text().replace(
            '"""" celery settings for quorum queues """',
            '""" celery settings for quorum queues """',
        )
    )
    tox = source / "modules" / module / "tox.ini"
    tox.write_text(
        tox.read_text().replace(
            "[testenv:c1]\n",
            "[testenv:c1]\ninstall_command = python /opt/weko-ci/install_dependencies.py {opts} {packages}\n",
            1,
        )
    )


def runtime():
    from jinja2 import Environment

    instance = Path("/home/invenio/.virtualenvs/invenio/var/instance")
    for name in ("conf", "assets", "static", "data"):
        (instance / name).mkdir(parents=True, exist_ok=True)
    template = Environment()
    template.globals["environ"] = os.getenv
    rendered = template.from_string(
        Path("/code/scripts/instance.cfg").read_text()
    ).render()
    (instance / "conf/invenio.cfg").write_text(rendered)
    (instance / "invenio.cfg").symlink_to("conf/invenio.cfg")

    def search(method, path, payload):
        auth = base64.b64encode(
            ("admin:" + os.environ["CI_SEARCH_ADMIN_PASSWORD"]).encode()
        )
        request = Request(
            "https://opensearch:9200/_plugins/_security/api/" + path,
            data=json.dumps(payload).encode(),
            method=method,
            headers={
                "Authorization": "Basic " + auth.decode(),
                "Content-Type": "application/json",
            },
        )
        with urlopen(
            request, context=ssl._create_unverified_context(), timeout=30
        ) as response:
            return json.load(response)

    user = os.environ["INVENIO_OPENSEARCH_USER"]
    search(
        "PUT",
        "internalusers/" + user,
        {
            "password": os.environ["INVENIO_OPENSEARCH_PASS"],
            "backend_roles": ["admin"],
        },
    )
    for role in ("all_access", "security_rest_api_access"):
        search(
            "PUT", "rolesmapping/" + role, {"backend_roles": ["admin"], "users": [user]}
        )


if __name__ == "__main__":
    if len(sys.argv) == 3:
        checkout(sys.argv[1], Path(sys.argv[2]))
    else:
        runtime()
