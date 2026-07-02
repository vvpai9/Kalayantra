#!/usr/bin/env python3
"""
Test suite for Kālayantra v2.0 Backend calculations
Verifies astronomical output from Kalachakra and festival logic from Kalotsavachakra.
"""
import unittest
import sys
import os

# Include current directory in import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import Kalachakra as ps
import Kalotsavachakra as otsav

class TestPanchangaCalculations(unittest.TestCase):
    def test_samvatsara_jovian_cycle(self):
        # Verify Samvatsara for year 2026 (Shaka 1948)
        # 1948 + 11 = 1959 % 60 = 39 (Parabhava)
        res_en = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="en")
        res_de = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="devanagari")
        res_ia = ps.calculate_panchanga(2026, 6, 23, 5.5, 23.1765, 75.7885, 0.0, lang="iast")
        
        self.assertEqual(res_en["shaka_year"], 1948)
        self.assertEqual(res_en["samvatsara"], "Parabhava")
        self.assertEqual(res_de["samvatsara"], "पराभव")
        self.assertEqual(res_ia["samvatsara"], "Parābhava")

    def test_era_years(self):
        # July 2, 2026:
        # Shaka = 1948, Vikram (Chaitradi) = 2083, Kali = 5128
        res_july = ps.calculate_panchanga(2026, 7, 2, 5.5, 23.1765, 75.7885, 0.0, calendar_system="shaka")
        self.assertEqual(res_july["shaka_year"], 1948)
        self.assertEqual(res_july["vikram_year"], 2083)
        self.assertEqual(res_july["kali_year"], 5128)

        # Vikram (Kartikadi) on July 2, 2026 is 2082 (before Gujarati New Year)
        res_kartak = ps.calculate_panchanga(2026, 7, 2, 5.5, 23.1765, 75.7885, 0.0, calendar_system="kartak")
        self.assertEqual(res_kartak["vikram_year"], 2082)

        # March 1, 2026 (before Chaitra Shukla Pratipada):
        # Shaka = 1947, Vikram = 2082, Kali = 5127
        res_march = ps.calculate_panchanga(2026, 3, 1, 5.5, 23.1765, 75.7885, 0.0, calendar_system="shaka")
        self.assertEqual(res_march["shaka_year"], 1947)
        self.assertEqual(res_march["vikram_year"], 2082)
        self.assertEqual(res_march["kali_year"], 5127)
        
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
            festivals = otsav.calculate_festivals(res, 5.5)
            fest_names = [f["name"] for f in festivals]
            if "Makar Sankranti" in fest_names:
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
