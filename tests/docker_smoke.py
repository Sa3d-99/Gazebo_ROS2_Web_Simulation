#!/usr/bin/env python3
"""Opt-in integration test of a built image; no third-party host packages needed."""
import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import subprocess
import time
import urllib.request
import uuid


def docker(*args, timeout=60, input=None):
    return subprocess.run(
        ["docker", *args], input=input, text=True, capture_output=True,
        timeout=timeout, check=True,
    ).stdout.strip()


def wait_healthy(name, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = json.loads(docker("inspect", "--format", "{{json .State}}", name))
        if not state["Running"]:
            raise AssertionError(f"Container exited: {state}")
        if state.get("Health", {}).get("Status") == "healthy":
            return
        time.sleep(2)
    raise AssertionError("Container did not become healthy")


# Capture the actual virtual desktop over RFB, using only the container's Python.
CAPTURE = r'''
import socket, struct, zlib, json
s=socket.create_connection(('127.0.0.1',5900),timeout=20)
def read(n):
    data=b''
    while len(data)<n:
        part=s.recv(n-len(data))
        if not part: raise RuntimeError('RFB disconnected')
        data+=part
    return data
assert read(12).startswith(b'RFB ')
s.sendall(b'RFB 003.008\n')
types=read(read(1)[0]); assert 1 in types
s.sendall(b'\x01'); assert read(4)==b'\0'*4
s.sendall(b'\x01')
w,h=struct.unpack('>HH',read(4)); read(16)
name=read(struct.unpack('>I',read(4))[0]).decode()
s.sendall(b'\x00\0\0\0'+struct.pack('>BBBBHHHBBB3x',32,24,0,1,255,255,255,16,8,0))
s.sendall(struct.pack('>BBHi',2,0,1,0))
s.sendall(struct.pack('>BBHHHH',3,0,0,0,w,h))
assert read(1)==b'\0'
_,count=struct.unpack('>BH',read(3))
pixels=bytearray(w*h*3)
for _ in range(count):
    x,y,rw,rh,encoding=struct.unpack('>HHHHi',read(12)); assert encoding==0
    raw=read(rw*rh*4)
    rgb=bytearray(rw*rh*3)
    rgb[0::3]=raw[2::4]; rgb[1::3]=raw[1::4]; rgb[2::3]=raw[0::4]
    for row in range(rh):
        dst=((y+row)*w+x)*3
        pixels[dst:dst+rw*3]=rgb[row*rw*3:(row+1)*rw*3]
colors=len(set(zip(pixels[0::3],pixels[1::3],pixels[2::3])))
assert colors>100, f'Desktop appears blank: {colors} colors'
def chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
scan=b''.join(b'\0'+pixels[row*w*3:(row+1)*w*3] for row in range(h))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
open('/tmp/gazebo-desktop.png','wb').write(png)
print(json.dumps({'width':w,'height':h,'colors':colors,'desktop':name}))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    prefix = "gazebo-smoke-" + uuid.uuid4().hex[:10]
    containers = []
    volume = prefix + "-worlds"
    result = {"image": args.image, "started_at": datetime.now(timezone.utc).isoformat(), "checks": {}}

    def passed(check, detail=True):
        result["checks"][check] = detail
        print(f"PASS {check}: {detail}", flush=True)

    def create(suffix, *extra):
        name = prefix + suffix
        containers.append(name)
        docker("run", "-d", "--name", name, "--shm-size=1g", "--stop-timeout=30",
               "-e", "RES=1280x720", *extra, args.image)
        return name

    try:
        docker("volume", "create", volume)
        meta = json.loads(docker("image", "inspect", args.image))[0]
        result.update(image_id=meta["Id"], architecture=meta["Architecture"], size_bytes=meta["Size"])
        name = create("-web", "-p", "127.0.0.1::8080", "-v", f"{volume}:/workspace/worlds")
        wait_healthy(name)
        passed("healthy_desktop")
        passed("platform", docker("exec", name, "bash", "/opt/gazebo-web/gazebo.sh", "check"))
        versions = docker("exec", name, "bash", "-c", 'source /opt/ros/*/setup.bash; dpkg-query -W -f=\'${Package}=${Version}\\n\' "ros-$ROS_DISTRO-ros-base" "ros-$ROS_DISTRO-ros-gz" "ros-$ROS_DISTRO-ros-gz-sim"')
        passed("installed_versions", versions.splitlines())
        binding = json.loads(docker("inspect", "--format", "{{json .NetworkSettings.Ports}}", name))
        port = int(binding["8080/tcp"][0]["HostPort"])
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/vnc.html", timeout=10) as response:
            assert response.status == 200 and b"noVNC" in response.read()
        passed("published_http_200")
        key = base64.b64encode(uuid.uuid4().bytes).decode()
        with socket.create_connection(("127.0.0.1", port), timeout=10) as sock:
            request = (f"GET /websockify HTTP/1.1\r\nHost: localhost:{port}\r\n"
                       "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                       f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
                       "Sec-WebSocket-Protocol: binary\r\n\r\n")
            sock.sendall(request.encode())
            assert b"101" in sock.recv(4096).split(b"\r\n")[0]
        passed("websocket_upgrade")
        packages = docker("exec", name, "bash", "-c", 'source /opt/ros/*/setup.bash; ros2 pkg prefix ros_gz_sim; ros2 pkg prefix ros_gz_bridge')
        passed("ros_integration_packages", packages.splitlines())
        topics = docker("exec", name, "bash", "-c", 'source /opt/ros/*/setup.bash; if command -v gz >/dev/null; then gz topic -l; else ign topic -l; fi', timeout=40)
        assert "/world/shapes/stats" in topics and "/world/shapes/pose/info" in topics, topics
        passed("simulation_topics", topics.splitlines())
        stats = docker("exec", name, "bash", "-c", 'source /opt/ros/*/setup.bash; if command -v gz >/dev/null; then cli=gz; else cli=ign; fi; timeout 25 "$cli" topic -e -t /world/shapes/stats -n 2', timeout=35)
        assert "sim_time" in stats and "iterations" in stats, stats
        iterations = [int(n) for n in re.findall(r"iterations: (\d+)", stats)]
        assert len(iterations) >= 2 and iterations[-1] > iterations[0], stats
        passed("simulation_publishes_stats", stats)
        windows = docker("exec", name, "bash", "-c", 'DISPLAY="$DISPLAY_NUM" xwininfo -root -tree')
        assert "Gazebo" in windows, windows
        passed("gazebo_gui_window")
        screenshot = json.loads(docker("exec", "-i", name, "python3", "-", input=CAPTURE))
        if args.output:
            path = args.output.with_suffix(".png")
            path.parent.mkdir(parents=True, exist_ok=True)
            docker("cp", f"{name}:/tmp/gazebo-desktop.png", str(path))
            screenshot["file"] = str(path)
        passed("rendered_desktop", screenshot)
        docker("exec", name, "bash", "-c", 'echo persistent-world > /workspace/worlds/smoke.txt')
        start = time.monotonic()
        docker("stop", "--time", "30", name, timeout=40)
        state = json.loads(docker("inspect", "--format", "{{json .State}}", name))
        assert state["ExitCode"] == 0 and not state["OOMKilled"], state
        assert "Desktop stopped." in docker("logs", name)
        passed("graceful_stop", {"seconds": round(time.monotonic()-start, 2), "exit_code": state["ExitCode"]})
        docker("start", name)
        wait_healthy(name)
        passed("restart")
        # The supervisor must exit on failure, including a service in a detached session.
        docker("exec", name, "pkill", "-x", "Xvfb")
        code = docker("wait", name, timeout=60)
        assert code == "1", code
        passed("service_failure_exits_nonzero")

        offline = create("-offline", "--network", "none", "-e", "VNC_PASSWORD=testpass", "-v", f"{volume}:/workspace/worlds")
        wait_healthy(offline)
        assert docker("exec", offline, "cat", "/workspace/worlds/smoke.txt") == "persistent-world"
        passed("world_volume_survives_new_container")
        assert "Installing" not in docker("logs", offline)
        passed("offline_start_no_install")
        security = docker("exec", offline, "python3", "-c", "import socket; s=socket.create_connection(('127.0.0.1',5900)); assert s.recv(12).startswith(b'RFB '); s.sendall(b'RFB 003.008\\n'); n=s.recv(1)[0]; types=s.recv(n); assert 2 in types and 1 not in types; print(list(types))")
        passed("vnc_requires_password", security)
        docker("stop", "--time", "30", offline, timeout=40)
        assert docker("inspect", "--format", "{{.State.ExitCode}}", offline) == "0"
        passed("offline_graceful_stop")
        command = docker("run", "--rm", "--network", "none", args.image, "ros2", "pkg", "prefix", "ros_gz_bridge")
        assert "/opt/ros/" in command
        passed("custom_command_ros_environment", command)
        mismatch = subprocess.run(
            ["docker", "run", "--rm", "--network", "none", "-e", "ROS_DISTRO=invalid", args.image],
            text=True, capture_output=True, timeout=20,
        )
        assert mismatch.returncode != 0 and "unsupported" in (mismatch.stdout + mismatch.stderr), mismatch
        passed("mismatched_ros_rejected")
        result["passed"] = True
    except Exception as exc:
        result["passed"] = False
        result["error"] = str(exc)
        for name in containers:
            try:
                print(docker("logs", "--tail", "70", name), flush=True)
                print(docker("exec", name, "bash", "-c", 'tail -n 50 "$LOG_DIR"/gazebo-gui.log'), flush=True)
            except Exception:
                pass
        raise
    finally:
        for name in containers:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)
        subprocess.run(["docker", "volume", "rm", volume], capture_output=True)
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
