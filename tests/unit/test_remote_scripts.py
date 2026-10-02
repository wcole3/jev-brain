import os
import subprocess
from pathlib import Path

import pytest

REMOTE = Path(__file__).parents[2] / "scripts" / "remote"
JOB_FILES = sorted((REMOTE / "jobs").glob("*.txt"))
COLLECTS = ["collect-calib", "collect-eval", "collect-index-dev"]


def job_names(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text().splitlines()]
    jobs = [line.split(":", 1) for line in lines if line and not line.startswith("#")]
    assert all(len(job) == 2 and job[0] and job[1].strip() for job in jobs), path
    return [name for name, _ in jobs]


@pytest.mark.parametrize("script", sorted(REMOTE.glob("*.sh")), ids=lambda p: p.name)
def test_scripts_parse(script):
    subprocess.run(["bash", "-n", str(script)], check=True)


def test_every_profile_has_a_job_file():
    assert [p.stem for p in JOB_FILES] == ["gemma-4-31b", "qwen3.6-27b", "qwen3.8-27b"]


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_job_files_parse_with_unique_names_starting_at_stack(path):
    names = job_names(path)
    index = [] if path.stem == "qwen3.6-27b" else ["index"]
    assert names == ["stack", "host-compare", *index, *COLLECTS]
    assert path.stem in path.read_text()


def test_index_job_resumes_the_box_run_tag():
    text = (REMOTE / "jobs" / "qwen3.8-27b.txt").read_text()
    assert "--run-dir .cache/index-runs/qwen3.8-27b/$(cat .cache/remote/run_tag)" in text


def queue(tmp_path, jobs: str) -> subprocess.CompletedProcess:
    jobfile = tmp_path / "jobs.txt"
    jobfile.write_text(jobs)
    env = os.environ | {"REMOTE_STATE": str(tmp_path / "remote")}
    command = ["bash", str(REMOTE / "queue.sh"), str(jobfile)]
    return subprocess.run(command, env=env, capture_output=True, text=True, check=False)


def test_queue_stops_at_a_failure_and_resumes_after_it(tmp_path):
    state, logs = tmp_path / "remote" / "state", tmp_path / "remote" / "logs"
    jobs = "# comment\n\nok: echo hi: there\nbad: false\nnever: true\n"
    assert queue(tmp_path, jobs).returncode != 0
    assert (state / "ok.done").exists() and (logs / "ok.log").read_text() == "hi: there\n"
    assert "exit=1" in (state / "bad.failed").read_text()
    assert not (state / "never.done").exists() and not (logs / "never.log").exists()
    assert not (state / "QUEUE_DONE").exists()

    assert queue(tmp_path, jobs.replace("bad: false", "bad: true")).returncode == 0
    log = (logs / "queue.log").read_text()
    assert log.count("== ok start") == 1 and log.count("== bad start") == 2
    assert "== bad FAILED" in log and "== bad done" in log
    assert (state / "bad.done").exists() and not (state / "bad.failed").exists()
    assert (state / "never.done").exists() and (state / "QUEUE_DONE").exists()
