import hashlib
import re
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
        self.assertIn("zando-st-george-monastery", names)
        self.assertIn("telefisi-fortress", names)

    def test_dezerters_bazaar_is_fully_removed(self):
        self.assertFalse((ROOT / "content" / "attractions" / "dezerters-bazaar.yml").exists())
        offenders = []
        needles = ("dezerter", "дезерт", "دزرت", "דזרט")
        for path in (ROOT / "content").rglob("*.yml"):
            text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8-sig").lower())
            if any(needle in text for needle in needles):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_attraction_car_categories_are_supported(self):
        invalid = []
        supported = {"economy", "suv", "offroad"}
        for path in (ROOT / "content" / "attractions").glob("*.yml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
            if data.get("car_category") not in supported:
                invalid.append((path.stem, data.get("car_category")))
        self.assertEqual(invalid, [])

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
            text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8-sig").lower())
            if any(claim.lower() in text for claim in stale_claims):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"stale fleet-size claims: {offenders}")

    def test_fuel_policy_is_named_consistently(self):
        """rental_policy.yml says full_to_full; the hub once called the same
        rule "same-to-same", which is the sentence an assistant quotes for
        "what is the fuel policy". No copy may name a different policy."""
        banned = ("same-to-same", "same to same", "level-to-level", "quarter tank")
        content = ROOT / "content"
        offenders = []
        for path in list((content / "pages").glob("*.yml")) + list((content / "settings").glob("*.yml")) \
                + list((content / "guides").glob("*.yml")):
            if path.name == "seo_ui.yml":      # the label table for every policy value, not prose
                continue
            text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8-sig").lower())
            if any(b in text for b in banned):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"fuel policy named inconsistently: {offenders}")

    def test_booking_copy_matches_the_stated_payment_policy(self):
        """Payment copy must agree with content/settings/rental_policy.yml.

        This test used to simply ban the phrase "no online payment", on the
        assumption that the site took payment online. The owner confirmed on
        2026-08-30 that it does not: a customer requests a car, RentUp confirms
        availability, and payment happens at pickup. Banning the true statement
        was therefore enforcing the wrong fact. The guard now works in both
        directions off the policy file, so it stays useful whichever way the
        business goes.
        """
        import yaml
        policy = yaml.safe_load(
            (ROOT / "content/settings/rental_policy.yml").read_text(encoding="utf-8"))
        prepay = (policy.get("cancellation") or {}).get("prepayment_required")

        # Regexes, not substrings: "no prepayment is required" contains
        # "prepayment is required", and flagging the correct sentence for
        # containing the incorrect one is how a guard starts lying.
        NEG = r"(?<!no )(?<!not )(?<!never )"
        denies_online_payment = [
            NEG + r"no online payment", r"ონლაინ გადახდა არ გვაქვს",
            r"онлайн-оплаты нет", r"بدون پرداخت آنلاین",
            r"אין תשלום מקוון", r"لا دفع إلكتروني",
        ]
        requires_prepayment = [
            r"(?<!no )(?<!without )prepayment is required",
            r"payment is required to confirm",
            r"booking is confirmed only (?:once|after) .{0,40}pay",
            r"ჯავშანი დასტურდება .{0,20}გადახდის შემდეგ",
            r"бронирование подтверждается после оплаты",
        ]
        forbidden = requires_prepayment if prepay is False else denies_online_payment
        why = ("rental_policy.yml says payment happens at pickup"
               if prepay is False else
               "rental_policy.yml says prepayment is required")

        offenders = []
        for path in (ROOT / "content").rglob("*.yml"):
            text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8-sig").lower())
            if any(re.search(pat, text) for pat in forbidden):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"{why}, but these pages say otherwise: {offenders}")


if __name__ == "__main__":
    unittest.main()
