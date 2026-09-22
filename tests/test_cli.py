import contextlib
import io
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


CLI = runpy.run_path(str(Path(__file__).resolve().parents[1] / "bin" / "ts-mullvad"))
NAMESPACE = CLI["main"].__globals__
NODE = "us-nyc-wg-501.mullvad.ts.net"
STATUS = {"Peer": {"node": {
    "DNSName": NODE, "ExitNodeOption": True, "Online": True,
    "Location": {"CountryCode": "US", "City": "New York"},
}}}


class LanPreferenceTests(unittest.TestCase):
    def setUp(self):
        self.preferences = {"--exit-node-allow-lan-access": "true"}
        self.calls = []

        def run(args, **kwargs):
            self.calls.append(args)
            # tailscale set retains preferences not explicitly supplied.
            for flag in args[2:]:
                key, value = flag.split("=", 1)
                self.preferences[key] = value

        self.patches = patch.dict(NAMESPACE, tailscale_bin=lambda: "tailscale",
                                  tailscale_status=lambda: STATUS, run=run)
        self.patches.start()
        self.addCleanup(self.patches.stop)

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(CLI["main"](list(args)), 0)

    def test_on_no_lan_resets_previously_enabled_access(self):
        self.invoke("on", "--node", NODE, "--no-lan")
        self.assertEqual(self.preferences["--exit-node-allow-lan-access"], "false")
        self.assertEqual(self.preferences["--exit-node"], NODE)

    def test_toggle_no_lan_resets_previously_enabled_access(self):
        self.invoke("toggle", "--node", NODE, "--no-lan")
        self.assertEqual(self.preferences["--exit-node-allow-lan-access"], "false")

    def test_default_on_reenables_access(self):
        self.preferences["--exit-node-allow-lan-access"] = "false"
        self.invoke("on", "--node", NODE)
        self.assertEqual(self.preferences["--exit-node-allow-lan-access"], "true")

    def test_off_only_clears_exit_node(self):
        self.invoke("off")
        self.assertEqual(self.calls, [["tailscale", "set", "--exit-node="]])


if __name__ == "__main__":
    unittest.main()
