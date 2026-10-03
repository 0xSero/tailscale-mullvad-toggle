import importlib.util
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


def load_tool():
    path = Path(__file__).resolve().parents[1] / "bin" / "ts-mullvad"
    loader = SourceFileLoader("ts_mullvad", str(path))
    spec = importlib.util.spec_from_loader("ts_mullvad", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def peer(name, city, country, ip):
    return {
        "DNSName": name,
        "HostName": name.split(".", 1)[0],
        "ExitNodeOption": True,
        "Tags": ["tag:mullvad-exit-node"],
        "Online": True,
        "TailscaleIPs": [ip],
        "Location": {"CountryCode": country, "City": city, "Priority": 1 if city == "New York" else 5},
    }


STATUS = {
    "Peer": {
        "nyc": peer("nyc.mullvad.ts.net", "New York", "US", "100.64.0.1"),
        "york": peer("york.mullvad.ts.net", "York", "GB", "100.64.0.2"),
    }
}


class CityMatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = load_tool()

    def test_york_does_not_select_new_york(self):
        self.assertFalse(self.tool.matches({"city": "New York"}, city="York"))
        chosen = self.tool.choose_node(STATUS, city="York")
        self.assertEqual(chosen["city"], "York")

    def test_new_york_still_selects_new_york(self):
        chosen = self.tool.choose_node(STATUS, city="New York")
        self.assertEqual(chosen["city"], "New York")

    def test_city_match_is_case_insensitive(self):
        self.assertTrue(self.tool.matches({"city": "New York"}, city="new york"))

    def test_country_match_is_unchanged(self):
        chosen = self.tool.choose_node(STATUS, country="US")
        self.assertEqual(chosen["city"], "New York")


if __name__ == "__main__":
    unittest.main()
