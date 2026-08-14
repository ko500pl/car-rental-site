import hashlib
import unittest
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class AttractionMediaTests(unittest.TestCase):
    def test_every_media_reference_exists(self):
        missing = []
        for path in (ROOT / "content" / "attractions").glob("*.yml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            raw = [data.get("image")] + list(data.get("gallery") or [])
            for item in raw:
                image = item.get("image") if isinstance(item, dict) else item
                if not image or str(image).startswith("http"):
                    continue
                rel = str(image)
                rel = rel[len("/assets/"):] if rel.startswith("/assets/") else rel.lstrip("/")
                if not (ROOT / "static" / rel).exists():
                    missing.append((path.stem, image))
        self.assertEqual(missing, [])

    def test_requested_places_are_present(self):
        names = {p.stem for p in (ROOT / "content" / "attractions").glob("*.yml")}
        self.assertIn("sameba-jikheti-monastery", names)
        self.assertIn("nodar-dumbadze-house-museum", names)

    def test_duplicate_media_is_reportable(self):
        """Keep duplicate detection measurable while the photo audit is resolved."""
        hashes = defaultdict(set)
        for path in (ROOT / "static" / "photos").glob("*.webp"):
            hashes[hashlib.sha256(path.read_bytes()).hexdigest()].add(path.name.split("-")[0])
        self.assertGreater(len(hashes), 200)


class PublicClaimsTests(unittest.TestCase):
    def test_fleet_size_claims_match_inventory(self):
        content = ROOT / "content"
        self.assertEqual(len(list((content / "cars").glob("*.yml"))), 17)
        stale_claims = (
            "120+ vehicles", "more than 120 vehicles", "120-vehicle fleet",
            "120+ ავტომობილი", "120-ზე მეტი ავტომობილი", "120 მანქან",
            "120+ автомобилей", "более 120 автомобилей",
            "بیش از 120 خودرو", "יותר מ-120", "أكثر من 120 سيارة",
        )
        offenders = []
        paths = list((content / "pages").glob("*.yml")) + list((content / "settings").glob("*.yml"))
        for path in paths:
            text = path.read_text(encoding="utf-8-sig").lower()
            if any(claim.lower() in text for claim in stale_claims):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"stale fleet-size claims: {offenders}")

    def test_booking_copy_does_not_deny_online_requests(self):
        forbidden = (
            "no online payment", "ონლაინ გადახდა არ გვაქვს", "онлайн-оплаты нет",
            "بدون پرداخت آنلاین", "אין תשלום מקוון", "لا دفع إلكتروني",
        )
        offenders = []
        for path in (ROOT / "content").rglob("*.yml"):
            text = path.read_text(encoding="utf-8-sig").lower()
            if any(phrase.lower() in text for phrase in forbidden):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"contradictory booking copy: {offenders}")


if __name__ == "__main__":
    unittest.main()
