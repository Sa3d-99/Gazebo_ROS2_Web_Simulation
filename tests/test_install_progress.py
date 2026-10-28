"""Installer regression checks using fake package tools, with no host apt changes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

from test_entrypoints import ROOT, executable


class InstallProgressTests(unittest.TestCase):
    def test_full_installer_saves_failure_output_and_never_reports_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "bin").mkdir()
            for name in ("install.sh", "install-utils.sh"):
                shutil.copy2(ROOT / name, directory / name)
            (directory / "requirements.txt").write_text("# No downloads in this test.\n")
            (directory / "gazebo.sh").write_text('''
gazebo_select_platform() { export ROS_DISTRO=humble; GAZEBO_RELEASE=Fortress; }
gazebo_install() { echo 'E: simulated ROS download failed' >&2; return 100; }
gazebo_verify_installation() { echo SHOULD_NOT_VERIFY; }
''')
            for command in ("git", "python3", "Xvfb", "x11vnc", "fluxbox", "websockify", "xdpyinfo", "apt-get"):
                executable(directory / "bin" / command, "#!/bin/sh\nexit 0\n")
            executable(directory / "bin/id", "#!/bin/sh\necho 0\n")
            env = {**os.environ, "PATH": f"{directory / 'bin'}:{os.environ['PATH']}",
                   "TMPDIR": str(directory), "LOG_DIR": str(directory / "logs")}
            result = subprocess.run(["bash", str(directory / "install.sh")], env=env,
                                    capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(result.returncode, 100, result.stdout + result.stderr)
            log = (directory / "logs/install.log").read_text()
            for output in (result.stdout, log):
                self.assertIn("E: simulated ROS download failed", output)
                self.assertIn("Installation stopped (exit 100)", output)
                self.assertNotIn("Installation complete", output)
                self.assertNotIn("SHOULD_NOT_VERIFY", output)

    def prepare(self, directory):
        (directory / "bin").mkdir()
        default_cache = directory / "default-cache"
        (default_cache / "partial").mkdir(parents=True)
        executable(directory / "bin/apt-get", '''
            #!/usr/bin/env python3
            import json, os, pathlib, shutil, sys
            args = sys.argv[1:]
            cache = next(a.split('=', 1)[1] for a in args if a.startswith('Dir::Cache::archives='))
            cache = pathlib.Path(cache)
            partial = cache / 'partial/package.deb'
            partial.write_text('package content')
            print('Get:1 package.deb 50% [1 MB]', flush=True)
            print('Package tool stderr is visible', file=sys.stderr, flush=True)
            # Reproduce a default-cache cleaner running during a download.
            shutil.rmtree(os.environ['DEFAULT_CACHE'])
            partial.rename(cache / 'package.deb')
            pathlib.Path(os.environ['APT_RECORD']).write_text(json.dumps({'args': args, 'cache': str(cache)}))
            if os.environ.get('APT_FAIL') == '1':
                print('E: simulated package download failure', file=sys.stderr)
                sys.exit(100)
            print('Setting up package...', flush=True)
        ''')
        return {**os.environ, "PATH": f"{directory / 'bin'}:{os.environ['PATH']}",
                "TMPDIR": str(directory), "LOG_DIR": str(directory / "logs"),
                "DEFAULT_CACHE": str(default_cache), "APT_RECORD": str(directory / "apt.json")}

    def run_install(self, env):
        return subprocess.run(
            ["bash", "-euc", 'source "$1"; SUDO=""; install_prepare_apt; '
             'install_apt install -y demo-package; echo INSTALL_SUCCEEDED',
             "test", str(ROOT / "install-utils.sh")], env=env,
            capture_output=True, text=True, timeout=10, check=False,
        )

    def test_progress_visible_and_private_cache_survives_default_cache_cleaner(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            env = self.prepare(directory)
            result = self.run_install(env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("50%", result.stdout)
            self.assertIn("Setting up package", result.stdout)
            self.assertIn("stderr is visible", result.stderr)
            record = json.loads((directory / "apt.json").read_text())
            self.assertNotEqual(record["cache"], env["DEFAULT_CACHE"])
            self.assertIn("quiet=0", record["args"])
            self.assertIn("Acquire::Retries=3", record["args"])
            self.assertIn("DPkg::Lock::Timeout=300", record["args"])
            self.assertNotIn("--fix-missing", record["args"])
            self.assertFalse(Path(record["cache"]).exists(), "Private downloads must be cleaned after exit")

    def test_failure_is_visible_and_does_not_report_success(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            env = {**self.prepare(directory), "APT_FAIL": "1"}
            result = self.run_install(env)
            self.assertEqual(result.returncode, 100, result.stdout + result.stderr)
            self.assertIn("simulated package download failure", result.stderr)
            self.assertIn("Installation stopped (exit 100)", result.stdout)
            self.assertNotIn("INSTALL_SUCCEEDED", result.stdout)
            record = json.loads((directory / "apt.json").read_text())
            self.assertFalse(Path(record["cache"]).exists())

    def test_another_installer_waits_for_the_existing_install(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            env = {**os.environ, "TMPDIR": str(directory), "LOG_DIR": str(directory)}
            holder = subprocess.Popen(
                ["bash", "-euc", 'source "$1"; install_prepare_apt; '
                 'echo first_started >> "$2/events"; touch "$2/ready"; '
                 'sleep 0.5; echo first_done >> "$2/events"',
                 "test", str(ROOT / "install-utils.sh"), str(directory)],
                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not (directory / "ready").exists():
                    self.assertIsNone(holder.poll())
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(0.01)
                result = subprocess.run(
                    ["bash", "-euc", 'source "$1"; install_prepare_apt; echo second_started >> "$2/events"',
                     "test", str(ROOT / "install-utils.sh"), str(directory)],
                    env=env, capture_output=True, text=True, timeout=5, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((directory / "events").read_text().splitlines(),
                                 ["first_started", "first_done", "second_started"])
                holder.wait(timeout=5)
                self.assertEqual(holder.returncode, 0)
            finally:
                if holder.poll() is None:
                    holder.terminate()
                holder.wait()
                holder.stderr.close()

    def test_ros_verification_rejects_missing_bridge(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "bin").mkdir()
            executable(directory / "bin/ros2", '''
                #!/bin/sh
                if [ "$3" = ros_gz_bridge ] && [ "$MISSING_BRIDGE" = 1 ]; then
                    echo 'Package not found: ros_gz_bridge' >&2
                    exit 1
                fi
                echo /opt/ros/test
            ''')
            setup = directory / "setup.bash"
            setup.write_text('export PATH="$VERIFY_BIN:$PATH"\n')
            for missing in ("0", "1"):
                with self.subTest(missing_bridge=missing):
                    result = subprocess.run(
                        ["bash", "-euc", 'source "$1"; ROS_DISTRO=humble; gazebo_verify_installation "$2"; echo VERIFIED',
                         "test", str(ROOT / "gazebo.sh"), str(setup)],
                        env={**os.environ, "VERIFY_BIN": str(directory / "bin"), "MISSING_BRIDGE": missing},
                        capture_output=True, text=True, timeout=5, check=False,
                    )
                    self.assertEqual(result.returncode, int(missing), result.stderr)
                    self.assertEqual("VERIFIED" in result.stdout, missing == "0")


if __name__ == "__main__":
    unittest.main()
