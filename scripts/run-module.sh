#!/usr/bin/env bash
set -euo pipefail

module=$1
source_dir=$(realpath "$2")
mkdir -p "reports/$module"
finish() {
    code=$?
    echo "$code" > "reports/$module/exit-code.txt"
}
trap finish EXIT
python3 scripts/prepare.py "$module" "$source_dir"

# OpenSearch requires this kernel setting; no runner resource caps are applied.
sudo sysctl -w vm.max_map_count=262144
docker compose up -d --wait --no-build
docker compose exec -T --user rabbitmq rabbitmq rabbitmqctl add_vhost queues_ut_ci
docker compose exec -T --user rabbitmq rabbitmq \
    rabbitmqctl set_permissions -p queues_ut_ci ci '.*' '.*' '.*'
docker compose exec -T -w "/code/modules/$module" runner python -m tox -e c1 --notest
docker compose exec -T runner \
    "/code/modules/$module/.tox/c1/bin/python" /opt/weko-ci/prepare.py
docker compose exec -T -w "/code/modules/$module" runner \
    python -m tox -e c1 -- tests --tb=short
