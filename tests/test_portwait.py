import socket
import subprocess
import sys
import threading
import time
import unittest

from portwait import wait_for_port


class WaitForPortTests(unittest.TestCase):
    def test_returns_true_when_port_is_already_listening(self):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        self.addCleanup(listener.close)

        self.assertTrue(wait_for_port("127.0.0.1", listener.getsockname()[1], timeout=0.2))

    def test_returns_false_when_port_stays_closed_until_timeout(self):
        reserved = socket.socket()
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
        reserved.close()

        self.assertFalse(wait_for_port("127.0.0.1", port, timeout=0.08, interval=0.01))

    def test_retries_until_a_listener_starts(self):
        reserved = socket.socket()
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
        reserved.close()

        accepted = threading.Event()

        def start_listener():
            time.sleep(0.06)
            with socket.socket() as listener:
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                listener.bind(("127.0.0.1", port))
                listener.listen()
                connection, _ = listener.accept()
                with connection:
                    accepted.set()

        starter = threading.Thread(target=start_listener, daemon=True)
        starter.start()
        self.assertTrue(wait_for_port("127.0.0.1", port, timeout=1, interval=0.01))
        self.assertTrue(accepted.wait(timeout=1))
        starter.join(timeout=1)

    def test_rejects_invalid_arguments(self):
        for args in [
            ("", 80, 1, 0.1),
            ("localhost", 0, 1, 0.1),
            ("localhost", 65536, 1, 0.1),
            ("localhost", 80, -1, 0.1),
            ("localhost", 80, 1, 0),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                wait_for_port(args[0], args[1], timeout=args[2], interval=args[3])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "portwait", *map(str, args)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_returns_zero_for_open_port(self):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        self.addCleanup(listener.close)

        result = self.run_cli("127.0.0.1", listener.getsockname()[1], "--timeout", "0.2")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ready", result.stdout.lower())

    def test_cli_returns_one_when_timeout_expires(self):
        reserved = socket.socket()
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
        reserved.close()

        result = self.run_cli("127.0.0.1", port, "--timeout", "0.05", "--interval", "0.01")

        self.assertEqual(result.returncode, 1)
        self.assertIn("timed out", result.stderr.lower())

    def test_cli_rejects_nonpositive_interval(self):
        result = self.run_cli("localhost", 80, "--interval", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("interval", result.stderr.lower())

    def test_cli_rejects_empty_host(self):
        result = self.run_cli("", 80, "--timeout", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("host", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
