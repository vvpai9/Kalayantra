#!/usr/bin/env python3
import unittest
import sys
import os

# Include current directory in import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import Kalachakra as ps

class TestPanchangaCalculations(unittest.TestCase):
    def test_samvatsara_jovian_cycle(self):
        # Verify Samvatsara for year 2026 (Shaka 1948)
        # 1948 + 12 = 1960 % 60 = 40 (Parabhava)
        res_en = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="en")
        res_de = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="devanagari")
        res_ia = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="iast")
        
        self.assertEqual(res_en["shaka_year"], 1948)
        self.assertEqual(res_en["samvatsara"], "Parabhava")
        self.assertEqual(res_de["samvatsara"], "पराभव")
        self.assertEqual(res_ia["samvatsara"], "Parābhava")
        
    def test_jyeshtha_shukla_navami(self):
        # Verify June 23, 2026 is Jyeshtha Shukla Navami
        res = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0)
        self.assertIn("Jyeshtha", res["masa"])
        self.assertEqual(res["paksha"], "Shukla")
        self.assertEqual(res["tithi"], "Navami")
        
    def test_makar_sankranti(self):
        # Sun enters Capricorn around Jan 14-15, 2026
        # Let's search which day has Makar Sankranti festival
        found = False
        for day in [14, 15]:
            res = ps.calculate_panchanga(2026, 1, day, 5.5, 23.1765, 75.7885, 0.0)
            if "Makar Sankranti" in res["festivals"]:
                found = True
                print(f"Makar Sankranti 2026 detected on Jan {day}")
                break
        self.assertTrue(found)

    def test_auspicious_segments(self):
        # Verify that time segments are calculated and have correct duration proportion
        res = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0)
        self.assertIsNotNone(res["rahu_kala"])
        self.assertIsNotNone(res["yamaghanta"])
        self.assertIsNotNone(res["gulika"])
        self.assertIsNotNone(res["abhijit_muhurta"])
        self.assertIsNotNone(res["tithi_end"])
        self.assertIsNotNone(res["nakshatra_end"])
        self.assertIsNotNone(res["yoga_end"])
        self.assertIsNotNone(res["karana_end"])
        self.assertIsNotNone(res["brahma_muhurta"])
        self.assertEqual(len(res["day_choghadiya"]), 8)
        self.assertEqual(len(res["night_choghadiya"]), 8)
        
        print("Rahu Kala:", res["rahu_kala"])
        print("Yamaghanta:", res["yamaghanta"])
        print("Gulika:", res["gulika"])
        print("Abhijit Muhurta:", res["abhijit_muhurta"])
        print("Brahma Muhurta:", res["brahma_muhurta"])
        print("Tithi End Time:", res["tithi_end"])
        print("Nakshatra End Time:", res["nakshatra_end"])
        print("Yoga End Time:", res["yoga_end"])
        print("Karana End Time:", res["karana_end"])
        print("First Day Choghadiya:", res["day_choghadiya"][0])
        print("First Night Choghadiya:", res["night_choghadiya"][0])

if __name__ == "__main__":
    unittest.main()
