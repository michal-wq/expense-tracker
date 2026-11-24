#!/bin/sh
set -eu

test_id=$(openssl rand -hex 12)
project="expense-tracker-test-$test_id"
POSTGRES_PASSWORD=$(openssl rand -hex 16)
export POSTGRES_PASSWORD
export POSTGRES_PORT=0

compose() {
    docker compose --env-file /dev/null --project-name "$project" --file compose.yaml "$@"
}

cleanup() {
    status=$?
    compose down --volumes || exit 1
    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

compose up --detach --wait --wait-timeout 60 db
address=$(compose port db 5432)
export TEST_DATABASE_URL="postgresql://expense_tracker:$POSTGRES_PASSWORD@$address/expense_tracker"
"$@"
