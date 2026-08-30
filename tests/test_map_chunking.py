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

    def test_standard_tour_can_define_origin_and_daily_budget(self):
        data = build.workspace_planner_data("ka")
        racha = next(tour for tour in data["standardTours"] if tour["s"] == "racha-mountain-loop")
        self.assertEqual(racha["origin"]["n"], "ქუთაისი")
        self.assertAlmostEqual(racha["origin"]["la"], 42.2679)
        self.assertEqual(racha["dailyHours"], 12.5)

    def test_client_has_stale_request_and_offline_guards(self):
        source = (ROOT / "static" / "workspace.js").read_text(encoding="utf-8")
        self.assertIn("AbortController", source)
        self.assertIn("request !== chunkRequest", source)
        self.assertIn("localStorage.setItem('do-map-chunk:'", source)
        self.assertIn("Object.assign(BY[rich.s], rich)", source)
        self.assertIn("setTimeout(function ()", source)
        self.assertIn("map.getBounds().pad(0.18)", source)
        self.assertIn("viewport.contains([p.la, p.lo])", source)

    def test_workspace_keeps_route_context_and_fits_without_network(self):
        source = (ROOT / "static" / "workspace.js").read_text(encoding="utf-8")
        self.assertIn("if (selected) return true", source)
        self.assertIn("Number(st.origin.la).toFixed(5)", source)
        self.assertIn("if (fitNext) { fitNext = false; map.fitBounds(L.latLngBounds(straight)", source)
        self.assertIn(";la=' + st.origin.la + ';lo=' + st.origin.lo", source)
        self.assertIn("var mtour = location.hash.match(/#tour=", source)
        self.assertNotIn("root.scrollIntoView({ behavior: 'smooth'", source)
        self.assertIn("blocked = !on && !ok", source)
        self.assertIn("(blocked ? ' disabled' : '')", source)
        self.assertIn("T.noFitNeed", source)
        self.assertIn("if (r.origin && isFinite(Number(r.origin.la))", source)
        self.assertIn("Number(r.dailyHours) || 8", source)

        planner = (ROOT / "static" / "planner.js").read_text(encoding="utf-8")
        self.assertNotIn("scrollIntoView({ behavior: 'smooth'", planner)

        explorer = (ROOT / "static" / "explorer.js").read_text(encoding="utf-8")
        self.assertIn("p.lat != null ? p.lat : p.la", explorer)

        theme = (ROOT / "theme.py").read_text(encoding="utf-8")
        self.assertIn("top:calc(100% + 6px)", theme)
        self.assertIn("min-height:146px", theme)


if __name__ == "__main__":
    unittest.main()
