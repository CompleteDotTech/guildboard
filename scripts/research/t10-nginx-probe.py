"""Run an owned, cached-image-only Nginx network experiment. Python stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
NGINX = "sha256:62ff2089abf5a9ed33bd232895bef5e22f7bb4b200675cec49a5ebc48e3d4ac8"
PYTHON = "sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70"


def docker(*args, input_text=None):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=30, input=input_text)
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
    return result


def run(control=None):
    token = "gb-t10-" + uuid.uuid4().hex[:12]
    backend, proxy = token + "-backend", token + "-proxy"
    label = "guildboard.t10.probe=" + token
    created = []
    report = {"observed_at": datetime.now(timezone.utc).isoformat(), "host": platform.platform(),
              "host_python": platform.python_version(), "images": {"nginx": NGINX, "python": PYTHON},
              "resource_scope": {"network": "network=none backend; nginx shares its owned network namespace", "published_ports": [], "mounts": [],
                                 "per_container": "0.5 CPU / 128MiB / 64 PIDs / nonroot / read-only / cap-drop ALL"}}
    for image in (NGINX, PYTHON):
        docker("image", "inspect", image)  # No pulls or installs; fail if absent.
    try:
        common = ["--pull=never", "--label", label, "--cpus", "0.5", "--memory", "128m", "--pids-limit", "64", "--user", "65534:65534", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m,mode=1777"]
        docker("create", "--name", backend, "--network", "none", *common, "--entrypoint", "python", PYTHON, "-c", "import time; time.sleep(3600)")
        created.append(("container", backend))
        docker("start", backend)
        docker("exec", "-i", backend, "python", "-c", "import sys; from pathlib import Path; Path('/tmp/probe.py').write_text(sys.stdin.read())", input_text=(ROOT / "scripts/research/t10-proxy-fixture.py").read_text())
        docker("exec", "-d", backend, "python", "/tmp/probe.py", "serve")
        docker("create", "--name", proxy, "--network", "container:" + backend, *common, "--entrypoint", "sleep", NGINX, "3600")
        created.append(("container", proxy))
        docker("start", proxy)
        config = (ROOT / "docs/research/t10-nginx-probe.conf").read_text()
        if control == "strip-upgrade":
            config = config.replace("proxy_set_header Upgrade $http_upgrade;", "proxy_set_header Upgrade '';" )
        elif control == "publish-private-assets":
            config = config.replace("location /private-assets/ { return 404; }", "location /private-assets/ { return 200 'exposed'; }")
        elif control is not None:
            raise ValueError("unknown negative control")
        docker("exec", "-i", proxy, "sh", "-c", "cat > /tmp/nginx.conf", input_text=config)
        check = docker("exec", proxy, "nginx", "-c", "/tmp/nginx.conf", "-t")
        report["nginx_config_check"] = (check.stdout + check.stderr).strip()
        docker("exec", "-d", proxy, "nginx", "-c", "/tmp/nginx.conf", "-g", "daemon off;")
        # Bounded readiness; successful traffic is required before the acceptance probe.
        readiness = "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8080/ready', timeout=1).status == 200"
        for attempt in range(20):
            try:
                docker("exec", backend, "python", "-c", readiness)
                break
            except subprocess.CalledProcessError:
                if attempt == 19:
                    raise
                time.sleep(0.1)
        version = docker("exec", proxy, "nginx", "-v")
        report["nginx_version"] = (version.stdout + version.stderr).strip()
        report["container_python"] = docker("exec", backend, "python", "--version").stdout.strip()
        try:
            report["result"] = json.loads(docker("exec", backend, "python", "/tmp/probe.py", "probe").stdout)
        except subprocess.CalledProcessError as error:
            expected = {"strip-upgrade": "HTTP/1.1 426", "publish-private-assets": "private-assets-not-public"}
            if control not in expected or expected[control] not in error.stderr:
                raise
            report["negative_control"] = {"variant": control, "detected": True, "failure": error.stderr.strip()}
        if control and "negative_control" not in report:
            raise AssertionError("unsafe negative control escaped the probe")
        report["fixture_hashes"] = {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
                                    for path in (ROOT / "docs/research/t10-nginx-probe.conf", ROOT / "scripts/research/t10-proxy-fixture.py")}
    finally:
        cleanup = []
        for kind, name in reversed(created):
            info = json.loads(docker(kind, "inspect", name).stdout)[0]
            labels = info.get("Config", {}).get("Labels", {}) if kind == "container" else info.get("Labels", {})
            if labels.get("guildboard.t10.probe") != token:
                raise RuntimeError("Ownership mismatch; refusing cleanup: " + name)
            docker(kind, "rm", *(["--force"] if kind == "container" else []), name)
            absent = subprocess.run(["docker", kind, "inspect", name], capture_output=True, text=True, timeout=10)
            if absent.returncode == 0 or "No such" not in absent.stderr:
                raise RuntimeError("Cleanup absence not verified: " + name)
            cleanup.append({"kind": kind, "name": name, "absence_verified": True})
        report["cleanup"] = cleanup
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--negative-control", choices=["strip-upgrade", "publish-private-assets"])
    args = parser.parse_args()
    try:
        report = run(args.negative_control)
    except subprocess.CalledProcessError as error:
        raise SystemExit("Owned Docker probe failed: " + error.stderr)
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
