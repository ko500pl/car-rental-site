from pathlib import Path
import unittest

import build


ROOT = Path(__file__).resolve().parents[1]


class MapChunkingTests(unittest.TestCase):
    def test_initial_index_is_complete_but_lightweight(self):
        full = build.explorer_points("ka")
        index = build.explorer_point_index("ka")
        self.assertEqual(len(index), len(full))
        self.assertEqual({point["s"] for point in index}, {point["s"] for point in full})
        self.assertTrue(all(len(point["names"]) == len(build.LANGS) for point in index))
        for heavy_key in ("img", "u", "h", "d", "un", "fe"):
            self.assertTrue(all(heavy_key not in point for point in index))

    def test_region_chunks_cover_every_place_once(self):
        full = build.explorer_points("ka")
        manifest, chunks = build.explorer_chunks("ka")
        chunk_points = [point for body in chunks.values() for point in body["pts"]]
        self.assertEqual(len(chunk_points), len(full))
        self.assertEqual(len({point["s"] for point in chunk_points}), len(full))
        self.assertEqual(sum(spec["count"] for spec in manifest.values()), len(full))
        for region, body in chunks.items():
            south, west, north, east = manifest[region]["bounds"]
            self.assertTrue(all(south <= point["la"] <= north for point in body["pts"]))
            self.assertTrue(all(west <= point["lo"] <= east for point in body["pts"]))
            self.assertIn(f"/data/points/ka/{region}.json?v=", manifest[region]["url"])

    def test_workspace_payload_does_not_duplicate_attractions(self):
        data = build.workspace_planner_data("ka")
        self.assertNotIn("a", data)
        self.assertIn("fleet", data)
        self.assertIn("standardTours", data)

    def test_client_has_stale_request_and_offline_guards(self):
        source = (ROOT / "static" / "workspace.js").read_text(encoding="utf-8")
        self.assertIn("AbortController", source)
        self.assertIn("request !== chunkRequest", source)
        self.assertIn("localStorage.setItem('do-map-chunk:'", source)
        self.assertIn("Object.assign(BY[rich.s], rich)", source)
        self.assertIn("setTimeout(function ()", source)
        self.assertIn("map.getBounds().pad(0.18)", source)
        self.assertIn("viewport.contains([p.la, p.lo])", source)


if __name__ == "__main__":
    unittest.main()
