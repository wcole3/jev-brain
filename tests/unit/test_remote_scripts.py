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


def test_job_commands_name_only_their_own_profile():
    for path in JOB_FILES:
        others = [p.stem for p in JOB_FILES if p != path]
        assert not [o for o in others if o in path.read_text()], path


def queue(tmp_path, jobs: str, name: str = "p") -> subprocess.CompletedProcess:
    jobfile = tmp_path / f"{name}.txt"
    jobfile.write_text(jobs)
    env = os.environ | {"REMOTE_STATE": str(tmp_path / "remote")}
    command = ["bash", str(REMOTE / "queue.sh"), str(jobfile)]
    return subprocess.run(command, env=env, capture_output=True, text=True, check=False)


def test_queue_stops_at_a_failure_and_resumes_after_it(tmp_path):
    state, logs = tmp_path / "remote" / "state" / "p", tmp_path / "remote" / "logs"
    jobs = "# comment\n\nok: echo hi: there\nbad: false\nnever: true\n"
    assert queue(tmp_path, jobs).returncode != 0
    assert (state / "ok.done").exists() and (logs / "p" / "ok.log").read_text() == "hi: there\n"
    assert "exit=1" in (state / "bad.failed").read_text()
    assert not (state / "never.done").exists() and not (logs / "p" / "never.log").exists()
    assert not (state / "QUEUE_DONE").exists()

    assert queue(tmp_path, jobs.replace("bad: false", "bad: true")).returncode == 0
    log = (logs / "queue.log").read_text()
    assert log.count("== ok start") == 1 and log.count("== bad start") == 2
    assert "== bad FAILED" in log and "== bad done" in log
    assert (state / "bad.done").exists() and not (state / "bad.failed").exists()
    assert (state / "never.done").exists() and (state / "QUEUE_DONE").exists()


def test_queue_runs_a_last_line_without_newline(tmp_path):
    assert queue(tmp_path, "a: true\nlast: true").returncode == 0
    assert (tmp_path / "remote" / "state" / "p" / "last.done").exists()


def test_queue_state_is_per_profile(tmp_path):
    assert queue(tmp_path, "ok: true\n", name="p1").returncode == 0
    assert queue(tmp_path, "ok: true\n", name="p2").returncode == 0
    assert (tmp_path / "remote" / "state" / "p2" / "ok.done").exists()
    assert (tmp_path / "remote" / "logs" / "queue.log").read_text().count("== ok start") == 2


FAKE_TMUX = """#!/usr/bin/env bash
# Windows live in $FAKE_TMUX, one name per line; new-session/new-window add one.
case $1 in
  list-windows) [[ -s $FAKE_TMUX ]] && cat "$FAKE_TMUX" ;;
  has-session) [[ -s $FAKE_TMUX ]] ;;
  new-session|new-window) while [[ $1 != -n ]]; do shift; done; echo "$2" >> "$FAKE_TMUX" ;;
esac
"""


def start(tmp_path, windows: str) -> tuple[list[str], Path]:
    repo, bin_dir = tmp_path / "repo", tmp_path / "bin"
    (repo / ".cache" / "remote" / "state" / "p").mkdir(parents=True)
    (repo / "scripts").symlink_to(REMOTE.parent)
    (repo / ".cache" / "remote" / "profile").write_text("p\n")
    (repo / ".cache" / "remote" / "state" / "bootstrap.done").write_text("p\n")
    stack_done = repo / ".cache" / "remote" / "state" / "p" / "stack.done"
    stack_done.touch()
    bin_dir.mkdir()
    (bin_dir / "tmux").write_text(FAKE_TMUX)
    (bin_dir / "tmux").chmod(0o755)
    (tmp_path / "windows").write_text(windows)
    env = os.environ | {"JEV_REPO": str(repo), "FAKE_TMUX": str(tmp_path / "windows"),
                        "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    subprocess.run(["bash", str(REMOTE / "start.sh")], env=env, check=True)
    assert (repo / ".cache" / "remote" / "run_tag").read_text().endswith("-vast\n")
    return (tmp_path / "windows").read_text().split(), stack_done


def test_start_opens_both_windows_on_a_fresh_boot(tmp_path):
    windows, stack_done = start(tmp_path, "")
    assert windows == ["telemetry", "queue"] and not stack_done.exists()


def test_start_reopens_a_finished_queue_window(tmp_path):
    windows, stack_done = start(tmp_path, "telemetry\n")
    assert windows == ["telemetry", "queue"] and not stack_done.exists()


def test_start_reopens_only_a_missing_telemetry_window(tmp_path):
    windows, stack_done = start(tmp_path, "queue\n")
    assert windows == ["queue", "telemetry"] and stack_done.exists()


def test_start_leaves_a_running_session_alone(tmp_path):
    windows, stack_done = start(tmp_path, "telemetry\nqueue\n")
    assert windows == ["telemetry", "queue"] and stack_done.exists()
