"""Real local proxy negative controls, opt-in Docker prerequisite; no image pulls."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("t10_probe", ROOT / "scripts/research/t10-nginx-probe.py")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class ActualNginxControls(unittest.TestCase):
    def test_upgrade_removal_is_detected(self):
        result = PROBE.run("strip-upgrade")
        self.assertTrue(result["negative_control"]["detected"])
        self.assertTrue(all(item["absence_verified"] for item in result["cleanup"]))

    def test_public_private_route_is_detected(self):
        result = PROBE.run("publish-private-assets")
        self.assertTrue(result["negative_control"]["detected"])
        self.assertTrue(all(item["absence_verified"] for item in result["cleanup"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
