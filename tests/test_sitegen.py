import unittest
from pathlib import Path

import build
from sitegen.validation import is_public, validate


class CurrencyTests(unittest.TestCase):
    def test_requested_rounding_examples(self):
        self.assertEqual(build.gel_to_usd(75), 30)
        self.assertEqual(build.gel_to_usd(145), 60)
        self.assertEqual(build.gel_to_usd(330), 130)

    def test_rental_price_tiers(self):
        car = {"price_1_6": 100, "price_7_29": 90, "price_30": 80}
        self.assertEqual(build.rental_total(car, 1), 100)
        self.assertEqual(build.rental_total(car, 6), 600)
        self.assertEqual(build.rental_total(car, 7), 630)
        self.assertEqual(build.rental_total(car, 30), 2400)


class PublishingTests(unittest.TestCase):
    def test_status_visibility(self):
        self.assertTrue(is_public({}))  # legacy records stay published
        self.assertTrue(is_public({"status": "published"}))
        self.assertFalse(is_public({"status": "draft"}))
        self.assertFalse(is_public({"status": "archived"}))

    def test_broken_route_reference_is_blocked(self):
        localized = {lang: {} for lang in ("ka", "en", "ru", "fa", "he", "ar")}
        report = validate(
            {"usd_rate": 2.6, "usd_rounding": 10}, {}, {}, {},
            {"route": {**localized, "waypoints": ["missing"]}}, {}, {})
        self.assertTrue(any("waypoint" in error for error in report.errors))


class ProductFeatureTests(unittest.TestCase):
    def test_every_explorer_point_has_multilingual_search_names(self):
        points = build.explorer_points("ka")
        self.assertGreater(len(points), 200)
        self.assertTrue(all(len(point["names"]) == len(build.LANGS) for point in points))

    def test_cycling_filter_has_real_candidates(self):
        points = build.explorer_points("ka")
        cycling = [point for point in points if point.get("bike")]
        self.assertGreater(len(cycling), 10)
        self.assertTrue(all(point["rd"] <= 2 for point in cycling))

    def test_georgia_boundary_is_packaged(self):
        boundary = Path("static/georgia-boundary.geojson")
        self.assertTrue(boundary.exists())
        self.assertGreater(boundary.stat().st_size, 10000)

    def test_account_and_map_scripts_parse_as_source_assets(self):
        for name in ("auth.js", "explorer.js", "planner.js", "community.js", "booking.js", "admin-bookings.js"):
            text = Path("static", name).read_text(encoding="utf-8")
            self.assertNotIn("configuration not found</", text)
            self.assertGreater(len(text), 500)
        booking = Path("static", "booking.js").read_text(encoding="utf-8")
        self.assertIn("https://wa.me/", booking)
        self.assertIn("new FormData(root)", booking)
        self.assertNotIn('collection(f.db, "bookings")', booking)

    def test_planner_start_search_controls_shared_map_origin(self):
        source = Path("build.py").read_text(encoding="utf-8")
        planner = Path("static", "planner.js").read_text(encoding="utf-8")
        explorer = Path("static", "explorer.js").read_text(encoding="utf-8")
        self.assertIn('id="startsearch" type="search"', source)
        self.assertIn('id="startoptions"', source)
        self.assertIn('FH_TRAVEL_EXPLORER.setOrigin(D.starts[index])', planner)
        self.assertIn('FH_TRAVEL_EXPLORER.setOrigin(start)', planner)
        self.assertIn('externalOrigin = {', explorer)
        self.assertIn('if (externalOrigin) return externalOrigin', explorer)

    def test_map_uses_progressive_count_clusters(self):
        explorer = Path("static", "explorer.js").read_text(encoding="utf-8")
        theme = Path("theme.py").read_text(encoding="utf-8")
        self.assertIn("function pixelGroups", explorer)
        self.assertIn("map.on('zoomend'", explorer)
        self.assertIn("clusterIcon(group.length", explorer)
        self.assertIn("var label = group.length", explorer)
        self.assertIn(".mapcluster", theme)

    def test_booking_admin_and_security_contract(self):
        rules = Path("firestore.rules").read_text(encoding="utf-8")
        admin = Path("static", "admin-bookings.js").read_text(encoding="utf-8")
        self.assertIn("request.auth.token.admin == true", rules)
        self.assertIn("request.resource.data.status == 'pending'", rules)
        self.assertIn("getIdTokenResult(true)", admin)
        self.assertIn('D.updateDoc(D.doc(db, "bookings"', admin)
        auth = Path("static", "auth.js").read_text(encoding="utf-8")
        self.assertIn('function renderMessages()', auth)
        self.assertIn('"conversations", card.dataset.conversation, "messages"', auth)
        community = Path("static", "community.js").read_text(encoding="utf-8")
        self.assertIn("data-join", community)
        self.assertIn("memberIds:(row.memberIds||[]).concat([u.uid])", community)

    def test_pwa_has_real_service_worker(self):
        app = Path("static", "app.js").read_text(encoding="utf-8")
        worker = Path("static", "sw.js").read_text(encoding="utf-8")
        manifest = Path("static", "manifest.webmanifest").read_text(encoding="utf-8")
        self.assertIn('register("/sw.js")', app)
        self.assertIn('self.addEventListener("fetch"', worker)
        self.assertIn('"display": "standalone"', manifest)
        self.assertIn('app-icon-192.png', manifest)
        self.assertIn('app-icon-maskable-512.png', manifest)
        self.assertIn('FH_INSTALL_APP', app)
        for icon in ("app-icon-180.png", "app-icon-192.png", "app-icon-512.png",
                     "app-icon-maskable-512.png"):
            path = Path("static", icon)
            self.assertTrue(path.exists(), str(path))
            self.assertGreater(path.stat().st_size, 1000)

    def test_header_exposes_android_and_ios_app_actions(self):
        source = Path("build.py").read_text(encoding="utf-8")
        app = Path("static", "app.js").read_text(encoding="utf-8")
        apk = Path("static", "downloads", "rentup-android.apk")
        self.assertIn('app-download', source)
        self.assertIn('rentup-android.apk', source)
        self.assertIn('data-ios-install', source)
        self.assertIn('FH_SHOW_IOS_INSTALL', app)
        self.assertTrue(apk.exists())
        self.assertGreater(apk.stat().st_size, 10_000)

    def test_safe_vehicle_floor_has_no_downgrade_fallback(self):
        planner = Path("static", "planner.js").read_text(encoding="utf-8")
        self.assertIn("c.rank >= needRank", planner)
        self.assertNotIn('filter(function (c) { return c.seats >= party; })', planner)

    def test_all_language_og_assets_exist(self):
        for lang in build.LANGS:
            path = Path("static", "og-" + lang + ".png")
            self.assertTrue(path.exists(), str(path))
            self.assertGreater(path.stat().st_size, 1000)

    def test_sitemap_uses_source_dates(self):
        source = Path("build.py").read_text(encoding="utf-8")
        self.assertIn("source_lastmod", source)
        self.assertNotIn("<lastmod>{TODAY}</lastmod>", source)

    def test_reusable_inquiry_and_admin_fields(self):
        source = Path("build.py").read_text(encoding="utf-8")
        cms = Path("admin", "config.yml").read_text(encoding="utf-8")
        self.assertIn("data-inquiry", source)
        for field in ("franchise", "insurance", "mileage_limit", "minimum_rental_days", "available"):
            self.assertIn("name: " + field, cms)

    def test_car_gallery_supports_cms_object_items(self):
        source = Path("build.py").read_text(encoding="utf-8")
        self.assertIn('g.get("image") if isinstance(g, dict) else g', source)

    def test_contact_page_uses_site_settings_not_duplicated_blocks(self):
        source = Path("build.py").read_text(encoding="utf-8")
        self.assertIn('[] if page == "contact" else sections', source)
        self.assertIn('SITE["mobile_e164"]', source)


if __name__ == "__main__":
    unittest.main()
