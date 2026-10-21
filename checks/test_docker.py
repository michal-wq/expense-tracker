"""Opt-in Docker checks, run with make docker-test."""

import json
import os
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest


def docker(*args):
    return subprocess.run(
        ["docker", *args], check=True, capture_output=True, text=True, timeout=30
    ).stdout.strip()


@pytest.fixture(scope="module")
def container_url():
    container = docker(
        "run",
        "--rm",
        "--detach",
        "--publish",
        "127.0.0.1::8000",
        os.environ.get("DOCKER_IMAGE", "expense-tracker:local"),
    )
    try:
        ports = json.loads(
            docker("inspect", "--format", "{{json .NetworkSettings.Ports}}", container)
        )
        port = ports["8000/tcp"][0]["HostPort"]
        base_url = f"http://127.0.0.1:{port}"
        deadline = time.monotonic() + 30
        while True:
            try:
                with urlopen(base_url, timeout=2) as response:
                    if response.status == 200:
                        break
            except (URLError, TimeoutError, ConnectionError):
                pass
            if time.monotonic() >= deadline:
                pytest.fail("Container did not respond within 30 seconds.")
            time.sleep(0.25)
        yield base_url
    finally:
        logs = subprocess.run(
            ["docker", "logs", container], capture_output=True, text=True, timeout=10
        )
        print(logs.stdout + logs.stderr)
        subprocess.run(["docker", "stop", "--timeout", "5", container], check=True, timeout=15)


@pytest.mark.parametrize(
    "path, mimetype",
    [
        ("/", "application/json"),
        ("/expenses", "text/html"),
        ("/static/style.css", "text/css"),
        ("/static/app.js", "text/javascript"),
    ],
)
def test_container_serves_http(container_url, path, mimetype):
    with urlopen(container_url + path, timeout=5) as response:
        assert response.status == 200
        assert response.headers.get_content_type() == mimetype
        assert response.read()
