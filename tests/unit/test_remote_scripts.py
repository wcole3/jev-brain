import os
import shlex
import shutil
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


PROFILE = "qwen3.8-27b"
IMAGE = "vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90"
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
    env = os.environ | {"PATH": path} | (env or {})
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


def test_push_dry_run_prints_every_step(tmp_path):
    repo = scratch_repo(tmp_path, git=True)
    out = local(repo, "push.sh", URL, PROFILE, "--dry-run")
    assert out.returncode == 0, out.stderr
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo, capture_output=True, text=True, check=True)
    assert head.stdout.strip() in out.stdout
    install, code, check, data, profile, start = commands(out.stdout)
    for step in (install, check, profile, start):
        assert step[:-1] == [*ssh_options(repo), HOST]
    assert "apt-get install -y -qq rsync tmux git" in install[-1]
    assert f"safe.directory {BOX}" in check[-1] and f"git -C {BOX} status --porcelain" in check[-1]
    assert profile[-1] == f"mkdir -p {BOX}/.cache/remote && echo {PROFILE} > {BOX}/.cache/remote/profile"
    assert start[-1] == f"cd {BOX} && setsid -f bash scripts/remote/start.sh > /dev/null 2>&1 < /dev/null"
    for step in (code, data):
        assert step[step.index("-e") + 1] == shlex.join(ssh_options(repo)) and "--delete" not in step
    excludes = {arg.removeprefix("--exclude=") for arg in code if arg.startswith("--exclude=")}
    hidden = {".cache", ".venv", ".firecrawl", "/secrets/*", ".superpowers", ".env", ".vscode"}
    assert hidden <= excludes and ".git" not in excludes and "secrets" not in excludes
    # rsync takes the first matching rule: the tracked .gitkeep goes, the rest of secrets/ stays here.
    assert code.index("--include=/secrets/.gitkeep") < code.index("--exclude=/secrets/*")
    assert code[-2:] == ["./", f"{HOST}:{BOX}/"]
    suite = [".cache/decision-index/rows-0.2.1.jsonl.gz", ".cache/decision-index/suite-0.2", ".cache/jevbench"]
    assert "--relative" in data and data[-4:] == [*suite, f"{HOST}:{BOX}/"]
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


def push_to_fake_box(tmp_path, *args: str, stray: bool = False) -> tuple[subprocess.CompletedProcess, Path, str]:
    """push.sh for real, but ssh runs here and rsync copies into a local dir standing in for the box."""
    repo = scratch_repo(tmp_path, git=True)
    (repo / ".gitignore").write_text(".cache/\nsecrets/*\n!secrets/.gitkeep\n")
    (repo / "secrets").mkdir()
    (repo / "secrets" / ".gitkeep").touch()
    (repo / "secrets" / "token").write_text("hf_secret")
    commit = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "secrets"]
    for git_args in (["add", ".gitignore", "secrets/.gitkeep"], commit):
        subprocess.run(["git", *git_args], cwd=repo, check=True)
    for path in ("decision-index/rows-0.2.1.jsonl.gz", "decision-index/suite-0.2/s", "jevbench/j",
                 f"index-runs/{PROFILE}/tag/shard-0/r", f"collect/{PROFILE}/c.jsonl", f"remote-boxes/{PROFILE}/run_tag",
                 *(f"remote-boxes/{PROFILE}/state/{PROFILE}/{name}.done" for name in MIRROR_STATE)):
        (repo / ".cache" / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / ".cache" / path).write_text("x\n")
    box = tmp_path / "box"
    if stray:
        box.mkdir()
        (box / "stray.txt").write_text("left by an earlier push")
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
    out, box, ssh_log = push_to_fake_box(tmp_path, stray=True)
    assert out.returncode != 0 and "stray.txt" in out.stderr
    assert not (box / ".cache" / "remote" / "profile").exists() and "start.sh" not in ssh_log


@needs_rsync
def test_push_restore_puts_back_runs_run_tag_and_index_collect_markers(tmp_path):
    out, box, _ = push_to_fake_box(tmp_path, "--restore")
    assert out.returncode == 0, out.stderr
    assert (box / ".cache" / "index-runs" / PROFILE / "tag" / "shard-0" / "r").exists()
    assert (box / ".cache" / "collect" / PROFILE / "c.jsonl").exists()
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
    assert runs[-3:] == [f".cache/index-runs/{PROFILE}", f".cache/collect/{PROFILE}", f"{HOST}:{BOX}/"]
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
# Log each call in $FAKE_RSYNC; the first call fails (box down); the 2nd pull of box state brings QUEUE_DONE.
printf '%q ' "$@" >> "$FAKE_RSYNC"
echo >> "$FAKE_RSYNC"
(( $(wc -l < "$FAKE_RSYNC") == 1 )) && [[ -n ${FAIL_FIRST:-} ]] && exit 255
dest=${!#}
[[ $dest == *remote-boxes* ]] || exit "${FAKE_EXIT:-0}"
mkdir -p "$dest/logs" "$dest/state/qwen3.8-27b"
printf 'one\ntwo\nthree\nfour\n' > "$dest/logs/queue.log"
(( $(grep -c 'remote-boxes/qwen3.8-27b/ $' "$FAKE_RSYNC") >= 2 )) && touch "$dest/state/qwen3.8-27b/QUEUE_DONE"
exit "${FAKE_EXIT:-0}"
"""


def pull(tmp_path, *args: str, fail_first: bool = False, exit_code: int = 0) -> tuple[subprocess.CompletedProcess, list[list[str]], Path]:
    repo = scratch_repo(tmp_path)
    (tmp_path / "bin" / "rsync").write_text(FAKE_RSYNC)
    calls = tmp_path / "rsync-calls"
    env = {"FAKE_RSYNC": str(calls), "FAKE_EXIT": str(exit_code)} | ({"FAIL_FIRST": "1"} if fail_first else {})
    out = local(repo, "pull.sh", URL, PROFILE, *args, env=env)
    return out, [shlex.split(line) for line in calls.read_text().splitlines()], repo


def test_pull_copies_results_runs_and_box_state_without_deleting(tmp_path):
    out, calls, repo = pull(tmp_path)
    assert out.returncode == 0, out.stderr
    assert [call[-2:] for call in calls[:3]] == [
        [f"{HOST}:{BOX}/docs/results/{PROFILE}", "docs/results/"],
        [f"{HOST}:{BOX}/.cache/collect/{PROFILE}", ".cache/collect/"],
        [f"{HOST}:{BOX}/.cache/index-runs/{PROFILE}", ".cache/index-runs/"],
    ]
    remote = f"{HOST}:{BOX}/.cache/remote"
    names = ["logs", "state", "telemetry.csv", "run_tag"]
    assert calls[3][-5:] == [*(f"{remote}/{name}" for name in names), f".cache/remote-boxes/{PROFILE}/"]
    assert len(calls) == 4
    for call in calls:
        assert call[call.index("-e") + 1] == shlex.join(ssh_options(repo)) and "--delete" not in call
    assert all("--update" in call for call in calls[:3]) and "--update" not in calls[3]
    assert out.stdout.splitlines()[-3:] == ["two", "three", "four"]
    assert (repo / "docs" / "results" / PROFILE).is_dir()


@pytest.mark.parametrize("code, ok", [(24, True), (23, False)])
def test_pull_tolerates_only_vanished_files(tmp_path, code, ok):
    out, calls, _ = pull(tmp_path, exit_code=code)
    assert (out.returncode == 0) == ok and len(calls) == (4 if ok else 1)


def test_pull_loop_survives_a_down_box_and_stops_after_a_pass_past_queue_done(tmp_path):
    stale = tmp_path / "repo" / ".cache" / "remote-boxes" / PROFILE / "state" / PROFILE / "QUEUE_DONE"
    stale.parent.mkdir(parents=True)
    stale.touch()
    out, calls, _ = pull(tmp_path, "--loop", "0", fail_first=True)
    assert out.returncode == 0, out.stderr
    assert "warning" in out.stderr
    # failed pass (1 call), pass without QUEUE_DONE, pass that pulls it, final pass (4 calls each)
    assert len(calls) == 13
