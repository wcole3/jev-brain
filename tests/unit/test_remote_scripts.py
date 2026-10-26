import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

from gateway.config import read_env_file
from gateway.orders import gate

REMOTE = Path(__file__).parents[2] / "scripts" / "remote"
JOB_FILES = sorted((REMOTE / "jobs").glob("*.txt"))


def job_names(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text().splitlines()]
    jobs = [line.split(":", 1) for line in lines if line and not line.startswith("#")]
    assert all(len(job) == 2 and job[0] and job[1].strip() for job in jobs), path
    return [name for name, _ in jobs]


@pytest.mark.parametrize("script", sorted(REMOTE.glob("*.sh")), ids=lambda p: p.name)
def test_scripts_parse(script):
    subprocess.run(["bash", "-n", str(script)], check=True)


# Box queues: stage 1 of the blurb_header default + round 4 orders campaign (2026-10-20); stage 2 (restack onward) follows.
JOBS = {
    profile: ("collect-calib", "collect-eval")
    for profile in ["gemma-4-31b", "gemma-4-31b-fp8", "qwen3.8-27b", "qwen3.8-27b-fp8", "qwen3.8-27b-nvfp4",
                    "qwen3.6-27b", "qwen3.6-27b-fp8"]
}
STACK_ONLY = ["gemma-4-12b", "gemma-4-12b-qat"]  # lower-tier profiles: a stack job, no campaign yet
JOBS |= {profile: () for profile in STACK_ONLY}
JOB_FILES = [p for p in JOB_FILES if p.stem not in STACK_ONLY]


def jobs_of(path: Path) -> dict[str, str]:
    return dict(line.split(": ", 1) for line in path.read_text().splitlines() if line and not line.startswith("#"))


def test_every_profile_has_a_job_file():
    assert sorted(p.stem for p in (REMOTE / "jobs").glob("*.txt")) == sorted(JOBS)


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_job_files_parse_with_unique_names_starting_at_stack(path):
    images = ["live-images"] if "live-images" in job_names(path) else []
    assert job_names(path)[: 1 + len(images) + 2] == ["stack", *images, *JOBS[path.stem]]
    assert jobs_of(path)["stack"] == f"bash scripts/remote/stack.sh up {path.stem}"


def collect_orders(profile: str) -> str:
    """The profile's live text setting; a gated one is fitted from an identity+reversed collect."""
    live = read_env_file(REMOTE.parents[1] / "profiles" / f"{profile}.env")["OPTION_ORDERS"]
    return "identity+reversed" if gate(live) is not None else live


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_collect_jobs_run_their_split_for_their_profile(path):
    for name, command in jobs_of(path).items():
        if name.startswith("collect-"):
            split = name.removeprefix("collect-")
            tail = f"scripts/collect.py --profile {path.stem} --split {split} --layouts blurb_header"
            assert command.endswith(f"{tail} --orders {collect_orders(path.stem)} --label blurb")


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_vision_profiles_check_images_before_collecting(path):
    names = job_names(path)
    vision = read_env_file(REMOTE.parents[1] / "profiles" / f"{path.stem}.env").get("SYSTEMONE_IMAGES") == "1"
    assert ("live-images" in names) == vision
    if vision:
        assert names.index("live-images") < names.index("collect-calib")
        stack = f"bash scripts/remote/stack.sh up {path.stem}"
        assert jobs_of(path)["live-images"] == f"{stack} && uv run pytest -m live tests/live/test_image_decisions.py -v"


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_index_jobs_resume_the_box_run_tag_and_fail_on_holes(path):
    for name, command in jobs_of(path).items():
        if name == "index":
            assert f"--profile {path.stem} --shards 4" in command
        if name.split("-")[0] == "index":  # index, index-before, index-after: each resumes its own tagged run dir
            tag = "" if name == "index" else name.removeprefix("index-") + "-"
            assert command.endswith(f"--run-dir .cache/index-runs/{path.stem}/{tag}$(cat .cache/remote/run_tag) --strict")
        if name.split("-")[0] == "latency":
            assert f"scripts/latency.py --profile {path.stem}" in command


def test_job_commands_name_only_their_own_profile():
    for path in JOB_FILES:
        named = set(re.findall(r"(?:qwen|gemma)[\w.-]*\w", path.read_text()))
        assert named == {path.stem}, path


def test_stack_patch_installs_the_patched_vllm_files(tmp_path):
    """Compose mounts docker/vllm/*.py over the image's files; boxes copy them the same way."""
    targets = {"rejection_sampler.py": "v1/worker/gpu/spec_decode", "scheduler.py": "v1/core/sched"}
    for name, sub in targets.items():
        (tmp_path / "vllm" / sub).mkdir(parents=True)
        (tmp_path / "vllm" / sub / name).write_text("stock\n")
    (tmp_path / "vllm" / "__init__.py").write_text("")
    env = os.environ | {"PYTHONPATH": str(tmp_path)}
    subprocess.run(["bash", str(REMOTE / "stack.sh"), "patch-vllm"], env=env, check=True, capture_output=True)
    for name, sub in targets.items():
        patched = REMOTE.parents[1] / "docker" / "vllm" / name
        assert (tmp_path / "vllm" / sub / name).read_text() == patched.read_text()


def test_stack_start_keeps_the_earlier_log(tmp_path):
    """A restart after a crash must not overwrite the log that shows the crash."""
    logs = tmp_path / ".cache" / "remote" / "logs"
    logs.mkdir(parents=True)
    (logs / "demo.log").write_text("crash\n")
    (tmp_path / "scripts" / "remote").mkdir(parents=True)
    functions = (REMOTE / "stack.sh").read_text().split("\ncase ")[0]  # everything but the command dispatch
    script = functions + "\nstart demo echo restarted\nwait\n"
    subprocess.run(["bash", "-c", script], cwd=tmp_path / "scripts" / "remote", check=True, capture_output=True)
    assert (logs / "demo.log").read_text() == "restarted\n"
    assert [p.read_text() for p in logs.glob("demo.*Z.log")] == ["crash\n"]


def queue(tmp_path, jobs: str, name: str = "p") -> subprocess.CompletedProcess:
    jobfile = tmp_path / f"{name}.txt"
    jobfile.write_text(jobs)
    env = os.environ | {"REMOTE_STATE": str(tmp_path / "remote")}
    command = ["bash", str(REMOTE / "queue.sh"), str(jobfile)]
    return subprocess.run(command, env=env, capture_output=True, text=True, check=False)


def test_queue_stops_at_a_failure_and_resumes_after_it(tmp_path):
    state, logs = tmp_path / "remote" / "state" / "p", tmp_path / "remote" / "logs"
    jobs = "# comment\n\nok: echo hi: there\nbad: echo try; false\nnever: true\n"
    assert queue(tmp_path, jobs).returncode != 0
    ok_log = (logs / "p" / "ok.log").read_text().splitlines()
    assert (state / "ok.done").exists() and ok_log[0].endswith("Z attempt 1") and ok_log[1:] == ["hi: there"]
    assert "exit=1" in (state / "bad.failed").read_text()
    assert not (state / "never.done").exists() and not (logs / "p" / "never.log").exists()
    assert not (state / "QUEUE_DONE").exists()

    assert queue(tmp_path, jobs.replace("bad: echo try; false", "bad: true")).returncode == 0
    log = (logs / "queue.log").read_text()
    assert log.count("== ok start") == 1 and log.count("== bad start") == 2
    assert log.count("== bad retry (exit 1)") == 1 and "== bad FAILED" in log and "== bad done" in log
    assert (state / "bad.done").exists() and not (state / "bad.failed").exists()
    assert (state / "never.done").exists() and (state / "QUEUE_DONE").exists()
    # every attempt is appended under its own header: two failed tries, then the run that worked
    bad_log = (logs / "p" / "bad.log").read_text()
    assert [line[-9:] for line in bad_log.splitlines() if "attempt" in line] == ["attempt 1", "attempt 2", "attempt 1"]
    assert bad_log.count("try\n") == 2


def test_queue_retries_a_failed_job_once(tmp_path):
    flag = tmp_path / "failed-once"
    assert queue(tmp_path, f"flaky: [ -f {flag} ] || {{ touch {flag}; false; }}\n").returncode == 0
    state, log = tmp_path / "remote" / "state" / "p", (tmp_path / "remote" / "logs" / "queue.log").read_text()
    assert "== flaky retry (exit 1)" in log and "FAILED" not in log
    assert (state / "flaky.done").exists() and not (state / "flaky.failed").exists()


def test_queue_clears_a_stale_queue_done_when_it_starts(tmp_path):
    state = tmp_path / "remote" / "state" / "p"
    state.mkdir(parents=True)
    (state / "QUEUE_DONE").touch()
    assert queue(tmp_path, "bad: false\n").returncode != 0
    assert not (state / "QUEUE_DONE").exists()


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
  new-session|new-window) while [[ $1 != -n ]]; do shift; done; echo "$2" >> "$FAKE_TMUX"
    printf '%s %s\n%s\n' "${FROM_IMAGE:-unset}" "${KEPT:-unset}" "$PATH" > "$FAKE_TMUX.env" ;;
esac
"""


def start(tmp_path, windows: str, extra: dict | None = None) -> tuple[list[str], Path]:
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
                        "PATH": f"{bin_dir}:{os.environ['PATH']}", "JEV_PID1_ENVIRON": str(tmp_path / "no-environ")}
    subprocess.run(["bash", str(REMOTE / "start.sh")], env=env | (extra or {}), check=True)
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


def test_start_takes_missing_variables_from_the_image_environment(tmp_path):
    """Over ssh, start.sh lacks the image's Docker ENV; PID 1 has it. Variables already set win."""
    environ = tmp_path / "environ"
    image_path = f"/image/cuda/bin:{tmp_path / 'bin'}:/image/cuda/bin"
    environ.write_bytes(f"FROM_IMAGE=cuda=1\0KEPT=image\0bad.name=x\0PATH={image_path}\0".encode())
    start(tmp_path, "", {"JEV_PID1_ENVIRON": str(environ), "KEPT": "ours"})
    values, path = (tmp_path / "windows.env").read_text().splitlines()
    assert values == "cuda=1 ours"
    # PATH is set over ssh too, so the image's missing dirs are appended once, after ours.
    assert path == f"{tmp_path / 'bin'}:{os.environ['PATH']}:/image/cuda/bin"


def test_start_runs_without_a_readable_image_environment(tmp_path):
    windows, _ = start(tmp_path, "", {"KEPT": "ours"})
    assert windows == ["telemetry", "queue"] and (tmp_path / "windows.env").read_text().splitlines()[0] == "unset ours"


def test_start_marks_a_failed_bootstrap_until_one_succeeds(tmp_path):
    """start.sh with a stand-in bootstrap.sh that exits $BOOT_EXIT; the real start.sh and queue.sh."""
    repo, remote = tmp_path / "repo", tmp_path / "repo" / ".cache" / "remote"
    (repo / "scripts" / "remote").mkdir(parents=True)
    for name in ("start.sh", "queue.sh"):
        (repo / "scripts" / "remote" / name).symlink_to(REMOTE / name)
    (repo / "scripts" / "remote" / "bootstrap.sh").write_text("exit $BOOT_EXIT\n")
    remote.mkdir(parents=True)
    (remote / "profile").write_text("p\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "tmux").write_text(FAKE_TMUX)
    (bin_dir / "tmux").chmod(0o755)
    (tmp_path / "windows").touch()
    env = os.environ | {"JEV_REPO": str(repo), "FAKE_TMUX": str(tmp_path / "windows"),
                        "PATH": f"{bin_dir}:{os.environ['PATH']}", "JEV_PID1_ENVIRON": str(tmp_path / "no-environ")}
    assert subprocess.run(["bash", str(REMOTE / "start.sh")], env=env | {"BOOT_EXIT": "7"}, check=False).returncode
    assert "exit=7" in (remote / "state" / "bootstrap.failed").read_text()
    assert (tmp_path / "windows").read_text() == ""
    subprocess.run(["bash", str(REMOTE / "start.sh")], env=env | {"BOOT_EXIT": "0"}, check=True)
    assert not (remote / "state" / "bootstrap.failed").exists()
    assert (tmp_path / "windows").read_text().split() == ["telemetry", "queue"]


FAKE_UV = """#!/usr/bin/env bash
# Log each call; `index_suite.py setup` installs $FAKE_HARNESS; fetch_model fails its first $FETCH_FAILS calls.
echo "uv $*" >> "$FAKE_LOG"
case $* in
  *"index_suite.py setup"*) mkdir -p .cache/decision-index-venv/bin && cp "$FAKE_HARNESS" .cache/decision-index-venv/bin/python ;;
  *fetch_model.py*) (( $(grep -c fetch_model "$FAKE_LOG") > ${FETCH_FAILS:-0} )) ;;
esac
"""
HARNESS_OK = "#!/usr/bin/env bash\n[[ $1 == -c ]] || echo '{\"match\": true}'\n"


def bootstrap(tmp_path, harness: str | None, fetch_fails: int = 0) -> tuple[subprocess.CompletedProcess, list[str], Path]:
    """bootstrap.sh with uv, sleep and the harness venv stubbed; `harness` is the venv python already there."""
    repo, bin_dir = tmp_path / "repo", tmp_path / "bin"
    repo.mkdir()
    (repo / "scripts").symlink_to(REMOTE.parent)
    bin_dir.mkdir()
    stubs = {"uv": FAKE_UV, "sleep": 'echo "sleep $*" >> "$FAKE_LOG"', "tmux": "", "rsync": "", "apt-get": REFUSE}
    for tool, text in stubs.items():
        (bin_dir / tool).write_text(text if text.startswith("#!") else f"#!/usr/bin/env bash\n{text}\n")
        (bin_dir / tool).chmod(0o755)
    (tmp_path / "harness").write_text(HARNESS_OK)
    (tmp_path / "harness").chmod(0o755)
    for path in (".cache/decision-index/src/partial", ".cache/decision-index/suite-0.3/keep"):
        (repo / path).parent.mkdir(parents=True)
        (repo / path).touch()
    if harness is not None:
        venv_python = repo / ".cache" / "decision-index-venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text(harness)
        venv_python.chmod(0o755)
    log = tmp_path / "log"
    log.touch()
    env = os.environ | {"PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_LOG": str(log),
                        "FAKE_HARNESS": str(tmp_path / "harness"), "FETCH_FAILS": str(fetch_fails)}
    out = subprocess.run(["bash", str(repo / "scripts" / "remote" / "bootstrap.sh"), "p"], env=env,
                         capture_output=True, text=True, check=False)
    return out, log.read_text().splitlines(), repo


SETUP = "uv run python scripts/index_suite.py setup"


def test_bootstrap_starts_over_a_harness_setup_left_half_done(tmp_path):
    out, log, repo = bootstrap(tmp_path, harness="#!/usr/bin/env bash\nexit 1\n")
    assert out.returncode == 0, out.stderr
    assert SETUP in log and not (repo / ".cache" / "decision-index" / "src" / "partial").exists()
    assert (repo / ".cache" / "decision-index" / "suite-0.3" / "keep").exists()
    assert (repo / ".cache" / "remote" / "state" / "bootstrap.done").read_text() == "p\n"


@pytest.mark.parametrize("harness", [None, HARNESS_OK], ids=["no venv", "working venv"])
def test_bootstrap_sets_the_harness_up_only_when_it_does_not_import(tmp_path, harness):
    out, log, _ = bootstrap(tmp_path, harness=harness)
    assert out.returncode == 0, out.stderr
    assert (SETUP in log) == (harness is None)


@pytest.mark.parametrize("fails, ok", [(2, True), (3, False)])
def test_bootstrap_retries_the_weight_download(tmp_path, fails, ok):
    out, log, repo = bootstrap(tmp_path, harness=HARNESS_OK, fetch_fails=fails)
    assert (out.returncode == 0) == ok
    assert sum("fetch_model.py --profile p" in line for line in log) == 3
    assert log.count("sleep 60") == 2 and ("uv run pytest -q" in log) == ok
    assert (repo / ".cache" / "remote" / "state" / "bootstrap.done").exists() == ok


PROFILE = "qwen3.8-27b"
IMAGE = "vllm/vllm-openai:v0.32.0@sha256:befccf0e7e4089aa23926bb6f887a85c0d46c2a99e6de5c5ffdf5cb7957c5b34"
URL, HOST, PORT = "ssh://root@203.0.113.7:41022", "root@203.0.113.7", "41022"
BOX = "/workspace/jev-brain"
# Stand-ins for the local side's network tools: refuse by default; FAKE_RSYNC (below) records calls.
REFUSE = "#!/usr/bin/env bash\necho \"$0 must not run in unit tests\" >&2\nexit 99\n"


def scratch_repo(tmp_path, git: bool = False) -> Path:
    repo, bin_dir = tmp_path / "repo", tmp_path / "bin"
    repo.mkdir(exist_ok=True)
    (repo / "scripts").symlink_to(REMOTE.parent)
    bin_dir.mkdir()
    for tool in ("ssh", "rsync", "vastai"):
        (bin_dir / tool).write_text(REFUSE)
        (bin_dir / tool).chmod(0o755)
    if git:
        commit = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "init"]
        for args in (["init", "-q"], ["add", "scripts"], commit):
            subprocess.run(["git", *args], cwd=repo, check=True)
    return repo


def local(repo: Path, name: str, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    path = f"{repo.parent / 'bin'}:{os.environ['PATH']}"
    env = os.environ | {"PATH": path, "JEV_SSH_KEY": "/nonexistent"} | (env or {})
    command = ["bash", str(repo / "scripts" / "remote" / name), *args]
    return subprocess.run(command, cwd=repo, env=env, capture_output=True, text=True, check=False)


def ssh_options(repo: Path) -> list[str]:
    known_hosts = repo / ".cache" / "remote-boxes" / PROFILE / "known_hosts"
    return ["ssh", "-p", PORT, "-o", "StrictHostKeyChecking=accept-new", "-o", f"UserKnownHostsFile={known_hosts}",
            "-o", "ServerAliveInterval=30"]


def commands(stdout: str) -> list[list[str]]:
    return [shlex.split(line) for line in stdout.splitlines() if line.startswith(("ssh ", "rsync "))]


def test_rent_dry_run_prints_the_vastai_command(tmp_path):
    out = local(scratch_repo(tmp_path), "rent.sh", "12345", PROFILE, "--dry-run")
    assert out.returncode == 0, out.stderr
    assert shlex.split(out.stdout) == [
        "vastai", "--raw", "create", "instance", "12345", "--image", IMAGE, "--disk", "250",
        "--ssh", "--direct", "--label", f"jev-{PROFILE}", "--cancel-unavail",
        "--onstart-cmd", "bash /workspace/jev-brain/scripts/remote/start.sh",
    ]


def test_rent_takes_a_disk_size(tmp_path):
    out = local(scratch_repo(tmp_path), "rent.sh", "12345", PROFILE, "--disk", "400", "--dry-run")
    assert "--disk 400 " in out.stdout


def fake_vastai(repo: Path, script: str) -> None:
    (repo.parent / "bin" / "vastai").write_text(f"#!/usr/bin/env bash\n{script}\n")


def test_rent_prints_the_new_instance_id(tmp_path):
    repo = scratch_repo(tmp_path)
    fake_vastai(repo, """echo '{"success": true, "new_contract": 4242}'""")
    out = local(repo, "rent.sh", "12345", PROFILE)
    assert out.returncode == 0, out.stderr
    assert "rented instance 4242" in out.stdout and "vastai ssh-url 4242" in out.stdout


@pytest.mark.parametrize("script", ["echo 'error: offer gone' >&2; exit 1", "echo nope", "echo '{\"success\": false}'"])
def test_rent_reports_a_failed_rent_without_a_traceback(tmp_path, script):
    repo = scratch_repo(tmp_path)
    fake_vastai(repo, script)
    out = local(repo, "rent.sh", "12345", PROFILE)
    assert out.returncode != 0 and "Traceback" not in out.stderr and "rented" not in out.stdout


@pytest.mark.parametrize("args", [["x", PROFILE], ["1", "nope"], ["1", PROFILE, "--disk"], ["1", PROFILE, "-x"]])
def test_rent_rejects_bad_arguments(tmp_path, args):
    out = local(scratch_repo(tmp_path), "rent.sh", *args, "--dry-run")
    assert out.returncode == 2 and not out.stdout


VISION_DATA = [".cache/decision-index-vision/src", ".cache/decision-index-vision/work/vision"]


@pytest.mark.parametrize("vision", [False, True], ids=["text", "vision"])
def test_push_dry_run_prints_every_step(tmp_path, vision):
    repo = scratch_repo(tmp_path, git=True)
    out = local(repo, "push.sh", URL, PROFILE, *(["--vision"] if vision else []), "--dry-run")
    assert out.returncode == 0, out.stderr
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True, text=True, check=True)
    assert head.stdout.strip() in out.stdout
    install, code, check, data, *kit, profile, start = commands(out.stdout)
    assert len(kit) == vision
    for step in (install, check, profile, start):
        assert step[:-1] == [*ssh_options(repo), HOST]
    assert "apt-get install -y -qq rsync tmux git" in install[-1]
    assert f"safe.directory {BOX}" in check[-1] and f"git -C {BOX} status --porcelain" in check[-1]
    assert profile[-1] == f"mkdir -p {BOX}/.cache/remote && echo {PROFILE} > {BOX}/.cache/remote/profile"
    assert start[-1] == f"cd {BOX} && setsid -f bash scripts/remote/start.sh > /dev/null 2>&1 < /dev/null"
    for step in (code, data, *kit):
        assert step[step.index("-e") + 1] == shlex.join(ssh_options(repo)) and "--delete" not in step
    excludes = {arg.removeprefix("--exclude=") for arg in code if arg.startswith("--exclude=")}
    hidden = {".cache", ".venv", ".firecrawl", "/secrets/*", ".superpowers", ".env", ".vscode"}
    assert hidden <= excludes and ".git" not in excludes and "secrets" not in excludes
    # rsync takes the first matching rule: the tracked .gitkeep goes, the rest of secrets/ stays here.
    assert code.index("--include=/secrets/.gitkeep") < code.index("--exclude=/secrets/*")
    assert code[-2:] == ["./", f"{HOST}:{BOX}/"]
    suite = [".cache/decision-index/rows-0.3.jsonl.gz", ".cache/decision-index/suite-0.3", ".cache/jevbench"]
    assert "--relative" in data and data[-4:] == [*suite, f"{HOST}:{BOX}/"]
    for step in kit:  # the kit source and Vision suite, at the same paths on the box
        assert "--relative" in step and step[-3:] == [*VISION_DATA, f"{HOST}:{BOX}/"]
    assert (repo / ".cache" / "remote-boxes" / PROFILE).is_dir()


def test_push_refuses_a_dirty_tree(tmp_path):
    repo = scratch_repo(tmp_path, git=True)
    (repo / "untracked").write_text("x")
    out = local(repo, "push.sh", URL, PROFILE, "--dry-run")
    assert out.returncode == 1 and "dirty" in out.stderr and not commands(out.stdout)


FAKE_BOX_SSH = r"""#!/usr/bin/env bash
# Run the remote command here with the box repo at $FAKE_BOX (git config kept beside it); never start the queue.
command=${!#}
echo "$command" >> "$FAKE_BOX.ssh-log"
[[ $command == *start.sh* ]] && exit 0
export GIT_CONFIG_GLOBAL=$FAKE_BOX.gitconfig
bash -c "${command//\/workspace\/jev-brain/$FAKE_BOX}"
"""
FAKE_BOX_RSYNC = r"""#!/usr/bin/env bash
exec "$REAL_RSYNC" "${@/#root@203.0.113.7:\/workspace\/jev-brain/$FAKE_BOX}"
"""
MIRROR_STATE = ["stack", "host-compare", "index", "collect-calib"]


def push_to_fake_box(tmp_path, *args: str, stray: str | None = None) -> tuple[subprocess.CompletedProcess, Path, str]:
    """push.sh for real, but ssh runs here and rsync copies into a local dir standing in for the box."""
    repo = scratch_repo(tmp_path, git=True)
    (repo / ".gitignore").write_text(".cache/\nsecrets/*\n!secrets/.gitkeep\n")
    (repo / "secrets").mkdir()
    (repo / "secrets" / ".gitkeep").touch()
    (repo / "secrets" / "token").write_text("hf_secret")
    commit = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "secrets"]
    for git_args in (["add", ".gitignore", "secrets/.gitkeep"], commit):
        subprocess.run(["git", *git_args], cwd=repo, check=True)
    for path in ("decision-index/rows-0.3.jsonl.gz", "decision-index/suite-0.3/s", "jevbench/j",
                 f"index-runs/{PROFILE}/tag/shard-0/r", f"collect/{PROFILE}/c.jsonl", f"vision-runs/{PROFILE}/full-tag/r",
                 f"remote-boxes/{PROFILE}/run_tag",
                 *(f"remote-boxes/{PROFILE}/state/{PROFILE}/{name}.done" for name in MIRROR_STATE)):
        (repo / ".cache" / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / ".cache" / path).write_text("x\n")
    box = tmp_path / "box"
    if stray:
        (box / stray).parent.mkdir(parents=True)
        (box / stray).write_text("left on the box")
    (tmp_path / "bin" / "ssh").write_text(FAKE_BOX_SSH)
    (tmp_path / "bin" / "rsync").write_text(FAKE_BOX_RSYNC)
    out = local(repo, "push.sh", URL, PROFILE, *args, env={"FAKE_BOX": str(box), "REAL_RSYNC": shutil.which("rsync")})
    log = Path(f"{box}.ssh-log")
    return out, box, log.read_text() if log.exists() else ""


needs_rsync = pytest.mark.skipif(shutil.which("rsync") is None, reason="needs a local rsync")


@needs_rsync
def test_push_leaves_the_box_tree_clean_and_secrets_here(tmp_path):
    out, box, ssh_log = push_to_fake_box(tmp_path)
    assert out.returncode == 0, out.stderr
    assert (box / "secrets" / ".gitkeep").exists() and not (box / "secrets" / "token").exists()
    assert (box / ".cache" / "jevbench" / "j").exists() and not (box / ".cache" / "index-runs").exists()
    assert (box / ".cache" / "remote" / "profile").read_text() == f"{PROFILE}\n" and "start.sh" in ssh_log
    status = subprocess.run(["git", "-C", str(box), "status", "--porcelain"], capture_output=True, text=True, check=True)
    assert status.stdout == ""


@needs_rsync
def test_push_stops_before_the_queue_when_the_box_tree_differs(tmp_path):
    out, box, ssh_log = push_to_fake_box(tmp_path, stray="stray.txt")
    assert out.returncode != 0 and "stray.txt" in out.stderr
    assert not (box / ".cache" / "remote" / "profile").exists() and "start.sh" not in ssh_log


@needs_rsync
def test_push_to_a_running_box_ignores_results_it_wrote(tmp_path):
    """Same rule as bench.git_revision: results written on the box don't make its code dirty."""
    out, _, ssh_log = push_to_fake_box(tmp_path, stray=f"docs/results/{PROFILE}/run/summary.md")
    assert out.returncode == 0, out.stderr
    assert "start.sh" in ssh_log


@needs_rsync
def test_push_restore_puts_back_runs_run_tag_and_index_collect_markers(tmp_path):
    out, box, _ = push_to_fake_box(tmp_path, "--restore")
    assert out.returncode == 0, out.stderr
    assert (box / ".cache" / "index-runs" / PROFILE / "tag" / "shard-0" / "r").exists()
    assert (box / ".cache" / "collect" / PROFILE / "c.jsonl").exists()
    assert (box / ".cache" / "vision-runs" / PROFILE / "full-tag" / "r").exists()
    assert (box / ".cache" / "remote" / "run_tag").read_text() == "x\n"
    markers = sorted(p.name for p in (box / ".cache" / "remote" / "state" / PROFILE).iterdir())
    assert markers == ["collect-calib.done", "index.done"]
    assert (box / ".cache" / "remote" / "profile").exists()


@pytest.mark.parametrize("flags", [["--restore", "--dry-run"], ["--dry-run", "--restore"]])
def test_push_restores_before_it_sets_the_profile(tmp_path, flags):
    repo = scratch_repo(tmp_path, git=True)
    (repo / ".git" / "info" / "exclude").write_text(".cache/\n")
    mirror = repo / ".cache" / "remote-boxes" / PROFILE
    (mirror / "state" / PROFILE).mkdir(parents=True)
    (mirror / "run_tag").write_text("t\n")
    for name in MIRROR_STATE:
        (mirror / "state" / PROFILE / f"{name}.done").touch()
    out = local(repo, "push.sh", URL, PROFILE, *flags)
    assert out.returncode == 0, out.stderr
    steps = commands(out.stdout)
    assert len(steps) == 10
    mkdir, runs, tag, markers, profile = steps[4:9]
    assert mkdir[-1] == f"mkdir -p {BOX}/.cache/remote/state/{PROFILE}"
    restored = [f".cache/{d}/{PROFILE}" for d in ("index-runs", "collect", "vision-runs")]
    assert runs[-4:] == [*restored, f"{HOST}:{BOX}/"]
    assert tag[-2:] == [f".cache/remote-boxes/{PROFILE}/run_tag", f"{HOST}:{BOX}/.cache/remote/run_tag"]
    state = f".cache/remote-boxes/{PROFILE}/state/{PROFILE}"
    assert markers[-3:] == [f"{state}/index.done", f"{state}/collect-calib.done", f"{HOST}:{BOX}/.cache/remote/state/{PROFILE}/"]
    assert profile[-1].endswith("/.cache/remote/profile")


def test_push_restore_needs_the_old_box_pulled(tmp_path):
    out = local(scratch_repo(tmp_path, git=True), "push.sh", URL, PROFILE, "--restore", "--dry-run")
    assert out.returncode == 1 and "run_tag" in out.stderr and not commands(out.stdout)


def test_push_rejects_an_unknown_flag(tmp_path):
    assert local(scratch_repo(tmp_path, git=True), "push.sh", URL, PROFILE, "--resume").returncode == 2


@pytest.mark.parametrize("url", ["root@h:22", "ssh://h:22", "ssh://root@h", "ssh://root@h:22x", "ssh://root@h:22/x"])
def test_push_and_pull_reject_a_bad_ssh_url(tmp_path, url):
    repo = scratch_repo(tmp_path, git=True)
    assert local(repo, "push.sh", url, PROFILE, "--dry-run").returncode == 2
    assert local(repo, "pull.sh", url, PROFILE).returncode == 2


@pytest.mark.parametrize("args", [[PROFILE, "--loop"], [PROFILE, "--loop", "x"], ["nope"], [PROFILE, "-x"]])
def test_pull_rejects_bad_arguments(tmp_path, args):
    assert local(scratch_repo(tmp_path), "pull.sh", URL, *args).returncode == 2


FAKE_RSYNC = """#!/usr/bin/env bash
# Log each call in $FAKE_RSYNC; the first call fails (box down); box state is a copy of $FAKE_REMOTE, and the
# 2nd pull of it brings QUEUE_DONE.
printf '%q ' "$@" >> "$FAKE_RSYNC"
echo >> "$FAKE_RSYNC"
(( $(wc -l < "$FAKE_RSYNC") == 1 )) && [[ -n ${FAIL_FIRST:-} ]] && exit 255
dest=${!#}
[[ $dest == *remote-boxes* ]] || exit "${FAKE_EXIT:-0}"
cp -r "$FAKE_REMOTE/." "$dest"
mkdir -p "$dest/state/qwen3.8-27b"
(( $(grep -c 'remote-boxes/qwen3.8-27b/ $' "$FAKE_RSYNC") >= 2 )) && touch "$dest/state/qwen3.8-27b/QUEUE_DONE"
exit "${FAKE_EXIT:-0}"
"""
QUEUE_LOG = "one\ntwo\nthree\nfour\n"


def pull(tmp_path, *args: str, fail_first: bool = False, exit_code: int = 0,
         box: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess, list[list[str]], Path]:
    """pull.sh against a stub rsync; `box` maps paths under the box's .cache/remote to their text."""
    repo = scratch_repo(tmp_path)
    (tmp_path / "bin" / "rsync").write_text(FAKE_RSYNC)
    (tmp_path / "bin" / "ssh").write_text("#!/usr/bin/env bash\necho \"$@\" >> \"$FAKE_RSYNC.ssh\"\n")
    remote = tmp_path / "box-remote"
    for path, text in ({"logs/queue.log": QUEUE_LOG} | (box or {})).items():
        (remote / path).parent.mkdir(parents=True, exist_ok=True)
        (remote / path).write_text(text)
    calls = tmp_path / "rsync-calls"
    env = {"FAKE_RSYNC": str(calls), "FAKE_EXIT": str(exit_code), "FAKE_REMOTE": str(remote)}
    out = local(repo, "pull.sh", URL, PROFILE, *args, env=env | ({"FAIL_FIRST": "1"} if fail_first else {}))
    return out, [shlex.split(line) for line in calls.read_text().splitlines()], repo


def test_pull_copies_results_runs_and_box_state_without_deleting(tmp_path):
    out, calls, repo = pull(tmp_path)
    assert out.returncode == 0, out.stderr
    assert [call[-2:] for call in calls[:5]] == [
        [f"{HOST}:{BOX}/docs/results/{PROFILE}", "docs/results/"],
        [f"{HOST}:{BOX}/docs/results/archive/{PROFILE}", "docs/results/archive/"],
        [f"{HOST}:{BOX}/.cache/collect/{PROFILE}", ".cache/collect/"],
        [f"{HOST}:{BOX}/.cache/index-runs/{PROFILE}", ".cache/index-runs/"],
        [f"{HOST}:{BOX}/.cache/vision-runs/{PROFILE}", ".cache/vision-runs/"],
    ]
    remote = f"{HOST}:{BOX}/.cache/remote"
    names = ["logs", "state", "telemetry.csv", "run_tag"]
    assert calls[5][-5:] == [*(f"{remote}/{name}" for name in names), f".cache/remote-boxes/{PROFILE}/"]
    assert len(calls) == 6
    for call in calls:
        assert call[call.index("-e") + 1] == shlex.join(ssh_options(repo)) and "--delete" not in call
    assert all("--update" in call for call in calls[:5]) and "--update" not in calls[5]
    assert out.stdout.splitlines()[-4:] == ["two", "three", "four", "bootstrap: running; job: none; failed: none"]
    assert (repo / "docs" / "results" / PROFILE).is_dir() and (repo / "docs" / "results" / "archive" / PROFILE).is_dir()


def test_pull_names_the_job_that_is_running(tmp_path):
    log = "t == stack start\nt == stack done\nt == index start\nt == index retry (exit 1)\n"
    out, _, _ = pull(tmp_path, box={"logs/queue.log": log, "state/bootstrap.done": PROFILE})
    assert out.returncode == 0 and out.stdout.splitlines()[-1] == "bootstrap: done; job: index; failed: none"


def test_pull_exits_3_on_a_failed_job(tmp_path):
    log = "t == index start\nt == index retry (exit 1)\nt == index FAILED (exit 1)\n"
    failed = {"logs/queue.log": log, "state/bootstrap.done": PROFILE, f"state/{PROFILE}/index.failed": "exit=1"}
    out, _, _ = pull(tmp_path, box=failed)
    assert out.returncode == 3 and out.stdout.splitlines()[-1] == "bootstrap: done; job: none; failed: index"


def test_pull_shows_the_start_log_when_bootstrap_failed(tmp_path):
    start_log = "".join(f"line {n}\n" for n in range(1, 8))
    out, _, _ = pull(tmp_path, box={"logs/start.log": start_log, "state/bootstrap.failed": "exit=1"})
    lines = out.stdout.splitlines()
    assert out.returncode == 3 and lines[-6:] == ["bootstrap: FAILED; job: none; failed: none",
                                                  *(f"line {n}" for n in range(3, 8))]


def test_pull_drops_alarms_the_box_has_cleared(tmp_path):
    state = tmp_path / "repo" / ".cache" / "remote-boxes" / PROFILE / "state"
    (state / PROFILE).mkdir(parents=True)
    for marker in ("bootstrap.done", "bootstrap.failed", f"{PROFILE}/index.failed"):
        (state / marker).write_text("old")
    (state / PROFILE / "index.done").write_text("kept")
    out, _, _ = pull(tmp_path)
    assert out.returncode == 0 and out.stdout.splitlines()[-1] == "bootstrap: running; job: none; failed: none"
    assert (state / PROFILE / "index.done").exists()


def test_pull_loop_keeps_going_and_reports_a_failure_every_pass(tmp_path):
    out, calls, _ = pull(tmp_path, "--loop", "0", box={f"state/{PROFILE}/collect-eval.failed": "exit=1"})
    assert out.returncode == 0 and len(calls) == 18
    assert out.stdout.count("failed: collect-eval") == 3


@pytest.mark.parametrize("code, ok", [(24, True), (23, False)])
def test_pull_tolerates_only_vanished_files(tmp_path, code, ok):
    out, calls, _ = pull(tmp_path, exit_code=code)
    assert (out.returncode == 0) == ok and len(calls) == (6 if ok else 1)


def test_pull_loop_survives_a_down_box_and_stops_after_a_pass_past_queue_done(tmp_path):
    stale = tmp_path / "repo" / ".cache" / "remote-boxes" / PROFILE / "state" / PROFILE / "QUEUE_DONE"
    stale.parent.mkdir(parents=True)
    stale.touch()
    out, calls, _ = pull(tmp_path, "--loop", "0", fail_first=True)
    assert out.returncode == 0, out.stderr
    assert "warning" in out.stderr
    # failed pass (1 call), pass without QUEUE_DONE, pass that pulls it, final pass (6 calls each)
    assert len(calls) == 19


def test_push_offers_the_vast_key_when_present(tmp_path):
    repo = scratch_repo(tmp_path, git=True)
    key = tmp_path / "id_vast"
    key.write_text("k")
    out = local(repo, "push.sh", URL, PROFILE, "--dry-run", env={"JEV_SSH_KEY": str(key)})
    assert out.returncode == 0, out.stderr
    assert all(f"-i {key} -o IdentitiesOnly=yes" in " ".join(c) for c in commands(out.stdout))


def test_pull_makes_the_box_dirs_before_fetching(tmp_path):
    out, _, _ = pull(tmp_path)
    ssh_calls = (tmp_path / "rsync-calls.ssh").read_text()
    assert out.returncode == 0 and "mkdir -p" in ssh_calls and f"{BOX}/.cache/collect/{PROFILE}" in ssh_calls
    assert f"{BOX}/.cache/vision-runs/{PROFILE}" in ssh_calls


STAGE_2 = ["restack", "latency-before", "latency-after", "vision-setup", "vision-latency", "index", "vision-full"]


@pytest.mark.parametrize("path", JOB_FILES, ids=lambda p: p.name)
def test_stage_2_follows_stage_1_with_vision_jobs_only_on_vision_profiles(path):
    names = job_names(path)
    vision = read_env_file(REMOTE.parents[1] / "profiles" / f"{path.stem}.env").get("SYSTEMONE_IMAGES") == "1"
    assert names[names.index("collect-eval") + 1 :] == [n for n in STAGE_2 if vision or not n.startswith("vision-")]
    assert len(names) == len(set(names))
