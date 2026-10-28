"""Exercise standalone routing without downloading packages or touching the host desktop."""
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import tarfile
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


def executable(path, content):
    path.write_text(textwrap.dedent(content).lstrip())
    path.chmod(0o755)


class EntrypointTests(unittest.TestCase):
    def environment(self, directory):
        env = dict(os.environ)
        for key in ("REPO", "BRANCH", "SIMULATOR", "VNC_PASSWORD", "ROS_DISTRO"):
            env.pop(key, None)
        env["PATH"] = f"{directory / 'bin'}:{env['PATH']}"
        return env

    def test_bootstrap_downloads_new_repository_and_forwards_ros_environment(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "bin").mkdir()
            archive_root = directory / "Gazebo_ROS2_Web_Simulation-main"
            archive_root.mkdir()
            executable(archive_root / "novnc.sh", '''
                #!/bin/bash
                printf '%s' "$ROS_DISTRO" > "$ENTRY_MARKER"
            ''')
            archive = directory / "repo.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                output.add(archive_root, arcname=archive_root.name)
            executable(directory / "bin/curl", '''
                #!/usr/bin/env python3
                import os, pathlib, shutil, sys
                args = sys.argv[1:]
                pathlib.Path(os.environ['URL_MARKER']).write_text(next(a for a in args if a.startswith('https://')))
                print('Download progress: 50%', file=sys.stderr)
                shutil.copyfile(os.environ['TEST_ARCHIVE'], args[args.index('-o') + 1])
            ''')
            env = {**self.environment(directory), "ROS_DISTRO": "jazzy",
                   "DEST": str(directory / "installed"), "TMPDIR": str(directory),
                   "TEST_ARCHIVE": str(archive),
                   "URL_MARKER": str(directory / "url"),
                   "ENTRY_MARKER": str(directory / "entry")}
            result = subprocess.run(["bash", str(ROOT / "bootstrap.sh")], env=env,
                                    capture_output=True, text=True, timeout=10, check=True)
            self.assertEqual((directory / "url").read_text(),
                             "https://codeload.github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/tar.gz/refs/heads/main")
            self.assertEqual((directory / "entry").read_text(), "jazzy")
            self.assertTrue((directory / "installed/novnc.sh").is_file())
            self.assertIn("Download progress: 50%", result.stderr)
            self.assertFalse(list(directory.glob("tmp.*")))

    def test_install_always_selects_and_installs_gazebo_without_mode_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "bin").mkdir()
            shutil.copy2(ROOT / "install.sh", directory / "install.sh")
            shutil.copy2(ROOT / "install-utils.sh", directory / "install-utils.sh")
            (directory / "requirements.txt").write_text("# No pip downloads in this fixture.\n")
            (directory / "gazebo.sh").write_text('''
gazebo_select_platform() { export ROS_DISTRO=humble; GAZEBO_RELEASE=Fortress; echo validate >> "$CALL_MARKER"; }
gazebo_install() { echo gazebo_install >> "$CALL_MARKER"; }
gazebo_verify_installation() { echo verify >> "$CALL_MARKER"; }
''')
            for command in ("git", "python3", "Xvfb", "x11vnc", "fluxbox", "websockify", "xdpyinfo", "apt-get"):
                executable(directory / "bin" / command, "#!/bin/sh\nexit 0\n")
            executable(directory / "bin/id", "#!/bin/sh\necho 0\n")
            env = {**self.environment(directory), "CALL_MARKER": str(directory / "calls"),
                   "TMPDIR": str(directory), "LOG_DIR": str(directory / "logs")}
            subprocess.run(["bash", str(directory / "install.sh")], env=env,
                           capture_output=True, text=True, timeout=10, check=True)
            self.assertEqual((directory / "calls").read_text().splitlines(), ["validate", "gazebo_install", "verify"])
            self.assertIn("Installation complete", (directory / "logs/install.log").read_text())

    def test_novnc_defaults_to_gazebo_and_passes_display_and_world(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "bin").mkdir()
            shutil.copy2(ROOT / "novnc.sh", directory / "novnc.sh")
            executable(directory / "install.sh", "#!/bin/sh\nexit 0\n")
            executable(directory / "gazebo.sh", '''
                #!/bin/bash
                gazebo_select_platform() { export ROS_DISTRO=humble; GAZEBO_RELEASE=Fortress; }
                if [[ "${BASH_SOURCE[0]}" == "$0" && "$1" == launch ]]; then
                    echo $$ >> "$PID_MARKER"
                    printf '%s|%s' "$DISPLAY" "$GAZEBO_ARGS" > "$LAUNCH_MARKER"
                    exec sleep 300
                fi
            ''')
            service = '''
                #!/usr/bin/env python3
                import os, pathlib, socket, sys, time
                with open(os.environ['PID_MARKER'], 'a') as output:
                    output.write(str(os.getpid()) + '\\n')
                name = pathlib.Path(sys.argv[0]).name
                if name in ('x11vnc', 'websockify'):
                    args = sys.argv[1:]
                    port = int(args[args.index('-rfbport') + 1] if name == 'x11vnc' else args[1])
                    sock = socket.socket()
                    sock.bind(('127.0.0.1', port))
                    sock.listen()
                time.sleep(300)
            '''
            for command in ("Xvfb", "fluxbox", "x11vnc", "websockify"):
                executable(directory / "bin" / command, service)
            for command in ("pkill", "xdpyinfo"):
                executable(directory / "bin" / command, "#!/bin/sh\nexit 0\n")
            sockets = [socket.socket(), socket.socket()]
            try:
                for sock in sockets:
                    sock.bind(("127.0.0.1", 0))
                vnc_port, web_port = (sock.getsockname()[1] for sock in sockets)
            finally:
                for sock in sockets:
                    sock.close()
            env = {**self.environment(directory), "LOG_DIR": str(directory / "logs"),
                   "DISPLAY_NUM": ":19999", "VNC_PORT": str(vnc_port), "WEB_PORT": str(web_port),
                   "GAZEBO_ARGS": "-r custom.sdf", "ISAAC_ROOT": str(directory / "must-not-use"),
                   "RUNPOD_POD_ID": "standalone-test", "PID_MARKER": str(directory / "pids"),
                   "LAUNCH_MARKER": str(directory / "launch")}
            try:
                result = subprocess.run(["bash", str(directory / "novnc.sh")], env=env,
                                        stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                        timeout=35, check=True)
                self.assertEqual((directory / "launch").read_text(), ":19999|-r custom.sdf")
                self.assertTrue((directory / "logs/gazebo-gui.pid").is_file())
                self.assertFalse((directory / "logs/isaac-gui.pid").exists())
                self.assertIn("Gazebo Fortress / ROS humble", result.stdout)
                self.assertIn(f"standalone-test-{web_port}.proxy.runpod.net", result.stdout)
            finally:
                if (directory / "pids").exists():
                    for pid in (directory / "pids").read_text().splitlines():
                        try:
                            os.killpg(int(pid), signal.SIGTERM)
                        except ProcessLookupError:
                            pass


if __name__ == "__main__":
    unittest.main()
