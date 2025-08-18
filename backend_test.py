#!/usr/bin/env python3
"""
تاقیکردنەوەی API ـی پشتەوە بۆ ئەپی ئیسلامی کوردی — دیزاینی تایبەتی کۆنسۆڵ
- تاقیکردنەوەی هەموو ئەندپۆینتە سەرەکییەکان
- سەرنج بەسەردا: کاتەکانی نوێژ بە فۆرماتی 12کاتژمێر و دیاریكردنی نوێژی ئێستا
- پەیوەندی و ڕێکخستن بە زمان: کوردی (ددۆزراوە)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

import requests

# URL ـی پشتەوە لە ژینگەی کارەکانی سیستەم بخوێنەوە، بە بنەڕەت: لوکال
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001/api")

# Test coordinates as specified in review request
TEST_COORDINATES = [
    ("Erbil (هەولێر)", {"lat": 36.1911, "lng": 44.0094}),
    ("Baghdad (بغداد)", {"lat": 33.3152, "lng": 44.3661}),
    ("Sulaymaniyah (سلێمانی)", {"lat": 35.5558, "lng": 45.4347}),
    ("Duhok (دهۆک)", {"lat": 36.8617, "lng": 42.9991})
]

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.use_color = True
        
    def log_pass(self, test_name):
        msg = f"✅ سەركەوتوو: {test_name}"
        print(f"{Color.GREEN}{msg}{Color.RESET}" if self.use_color else msg)
        self.passed += 1
        
    def log_fail(self, test_name, error):
        msg = f"❌ شکستی هێنا: {test_name} - {error}"
        print(f"{Color.RED}{msg}{Color.RESET}" if self.use_color else msg)
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        title = f"کورتەی تاقیکردنەوەکان: {self.passed}/{total} سەرکەوتوو"
        print(f"{Color.BOLD}{title}{Color.RESET}" if self.use_color else title)
        if self.errors:
            print("\nئەم تاقیکردنەوانە شکستی هێنا:")
            for error in self.errors:
                print(f"  - {error}")
        print("=" * 60)
        return self.failed == 0


def hr(title: str, icon: str = ""):
    bar = "─" * max(0, 48 - len(title))
    line = f"{icon} {title} {bar}"
    print(f"{Color.CYAN}{line}{Color.RESET}")


def get(url: str, timeout: float, retries: int = 2, backoff: float = 0.5) -> Optional[requests.Response]:
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            return requests.get(url, timeout=timeout)
        except Exception as e:
            last_exc = e
            time.sleep(backoff * (2 ** attempt))
    if last_exc:
        raise last_exc
    return None

def test_enhanced_prayer_times_api(results, base_url: str, timeout: float):
    """تاقیکردنەوەی کاتەکانی نوێژ بە فۆرماتی 12کاتژمێر و دیاریكردنی نوێژی ئێستا"""
    hr("تاقیکردنەوەی کاتەکانی نوێژ", "🕌")
    
    for city_name, coords in TEST_COORDINATES:
        try:
            url = f"{base_url}/prayer-times/{coords['lat']}/{coords['lng']}"
            response = get(url, timeout=timeout)
            
            if response.status_code != 200:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Status code {response.status_code}")
                continue
                
            data = response.json()
            print(f"\n📍 تاقیکردن: {city_name}")
            pretty = json.dumps(data, indent=2, ensure_ascii=False)
            print(f"   وەڵام:\n{pretty}")
            
            # Check all required prayer times (6 times as specified)
            required_times = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
            for prayer in required_times:
                if prayer not in data:
                    results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Missing {prayer} time")
                    continue
                    
                # Verify 12-hour format with Kurdish AM/PM indicators
                time_str = data[prayer]
                if not ("ب.ن" in time_str or "د.ن" in time_str):
                    results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Missing Kurdish AM/PM indicator in {prayer}: {time_str}")
                    continue
                    
                # Extract time part and verify format
                time_part = time_str.replace(" ب.ن", "").replace(" د.ن", "")
                try:
                    parsed_time = datetime.strptime(time_part, "%I:%M")
                    # In 12-hour format, valid hours are 1-12 (but strptime converts 12 to 0)
                    # So we need to check the original string for valid format
                    hour_str = time_part.split(":")[0]
                    hour_int = int(hour_str)
                    if hour_int < 1 or hour_int > 12:
                        results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Invalid 12-hour format for {prayer}: {time_str}")
                        continue
                except ValueError:
                    results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Invalid time format for {prayer}: {time_str}")
                    continue
                    
            # سەلماندنی گونجاوی
            fajr_time = data.get("fajr", "")
            dhuhr_time = data.get("dhuhr", "")
            maghrib_time = data.get("maghrib", "")
            
            # فەجڕ دەبێت ب.ن بێت
            if "د.ن" in fajr_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Fajr should be AM, got: {fajr_time}")
                continue
                
            # دهوور دەبێت د.ن بێت
            if "ب.ن" in dhuhr_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Dhuhr should be PM, got: {dhuhr_time}")
                continue
                
            # مەغرب دەبێت د.ن بێت
            if "ب.ن" in maghrib_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Maghrib should be PM, got: {maghrib_time}")
                continue
                
            # خانەی current_prayer هەبێت
            if "current_prayer" not in data:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", "Missing current_prayer field")
                continue
                
            current_prayer = data["current_prayer"]
            if current_prayer not in required_times:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Invalid current_prayer value: {current_prayer}")
                continue
                
            # Check additional required fields
            if "date" not in data:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", "Missing date field")
                continue
                
            if "city" not in data:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", "Missing city field")
                continue
                
            results.log_pass(f"Enhanced Prayer Times API ({city_name})")
            print(f"   ✅ All 6 prayer times with Kurdish AM/PM format")
            print(f"   ✅ Current prayer: {current_prayer}")
            print(f"   ✅ Reasonable prayer times verified")
            
        except Exception as e:
            results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Exception: {str(e)}")

def test_prayer_times_error_handling(results, base_url: str, timeout: float):
    """تاقیکردنەوەی هەڵەکانی API ـی کاتەکانی نوێژ بە هەڵەی چەقی ناوخۆ"""
    try:
        print(f"\n🔍 تاقیکردنەوەی هەڵەکانی نوێژ...")
        # Test with invalid coordinates
        url = f"{base_url}/prayer-times/999/999"
        response = get(url, timeout=timeout)
        
        # Should still return 200 but with fallback times
        if response.status_code != 200:
            results.log_fail("Prayer Times Error Handling", f"Status code {response.status_code} for invalid coords")
            return
            
        data = response.json()
        
        # Should still have all required fields even with invalid coords
        required_times = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
        for prayer in required_times:
            if prayer not in data:
                results.log_fail("Prayer Times Error Handling", f"Missing {prayer} time in fallback")
                return
                
        results.log_pass("Prayer Times Error Handling")
        
    except Exception as e:
        results.log_fail("Prayer Times Error Handling", f"Exception: {str(e)}")

def test_cities_api_regression(results, base_url: str, timeout: float):
    """تاقیکردنەوەی شارەکان بۆ ڕیگری لە دووبارە کێشە"""
    print(f"\n🏙️ تاقیکردنەوەی API ـی شارەکان...")
    
    # Test Kurdish cities
    try:
        response = get(f"{base_url}/cities/kurdish", timeout=timeout)
        
        if response.status_code != 200:
            results.log_fail("Kurdish Cities API", f"Status code {response.status_code}")
        else:
            data = response.json()
            if "cities" not in data or not isinstance(data["cities"], list):
                results.log_fail("Kurdish Cities API", "Invalid response structure")
            else:
                kurdish_city_names = [city.get("name", "") for city in data["cities"]]
                expected_kurdish = ["هەولێر", "سلێمانی", "دهۆک"]
                found_kurdish = any(name in kurdish_city_names for name in expected_kurdish)
                if found_kurdish:
                    results.log_pass("Kurdish Cities API")
                else:
                    results.log_fail("Kurdish Cities API", f"Expected Kurdish cities not found")
                    
    except Exception as e:
        results.log_fail("Kurdish Cities API", f"Exception: {str(e)}")
    
    # Test Arabic cities
    try:
        response = get(f"{base_url}/cities/arabic", timeout=timeout)
        
        if response.status_code != 200:
            results.log_fail("Arabic Cities API", f"Status code {response.status_code}")
        else:
            data = response.json()
            if "cities" not in data or not isinstance(data["cities"], list):
                results.log_fail("Arabic Cities API", "Invalid response structure")
            else:
                arabic_city_names = [city.get("name", "") for city in data["cities"]]
                expected_arabic = ["بغداد", "البصرة", "الموصل"]
                found_arabic = any(name in arabic_city_names for name in expected_arabic)
                if found_arabic:
                    results.log_pass("Arabic Cities API")
                else:
                    results.log_fail("Arabic Cities API", f"Expected Arabic cities not found")
                    
    except Exception as e:
        results.log_fail("Arabic Cities API", f"Exception: {str(e)}")

def test_qibla_direction_regression(results, base_url: str, timeout: float):
    """تاقیکردنەوەی ئاراستەی قیبلە"""
    print(f"\n🧭 تاقیکردنەوەی API ـی قیبلە...")
    
    test_cases = [
        ("Erbil", {"lat": 36.1911, "lng": 44.0094}),
        ("Baghdad", {"lat": 33.3152, "lng": 44.3661})
    ]
    
    for city_name, coords in test_cases:
        try:
            url = f"{base_url}/qibla/{coords['lat']}/{coords['lng']}"
            response = get(url, timeout=timeout)
            
            if response.status_code != 200:
                results.log_fail(f"Qibla Direction API ({city_name})", f"Status code {response.status_code}")
                continue
                
            data = response.json()
            
            # Check required fields
            required_fields = ["qibla_direction", "lat", "lng"]
            for field in required_fields:
                if field not in data:
                    results.log_fail(f"Qibla Direction API ({city_name})", f"Missing field '{field}'")
                    continue
                    
            # Verify qibla direction is a valid bearing (0-360)
            qibla_dir = data["qibla_direction"]
            if not isinstance(qibla_dir, (int, float)) or qibla_dir < 0 or qibla_dir >= 360:
                results.log_fail(f"Qibla Direction API ({city_name})", f"Invalid qibla direction: {qibla_dir}")
                continue
                
            results.log_pass(f"Qibla Direction API ({city_name})")
            
        except Exception as e:
            results.log_fail(f"Qibla Direction API ({city_name})", f"Exception: {str(e)}")

def test_duas_collection_regression(results, base_url: str, timeout: float):
    """تاقیکردنەوەی کۆمەڵەی دوعاکان"""
    print(f"\n📿 تاقیکردنەوەی کۆمەڵەی دوعاکان...")
    
    try:
        response = get(f"{base_url}/duas", timeout=timeout)
        
        if response.status_code != 200:
            results.log_fail("Duas Collection API", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        # Check for morning and evening duas
        if "morning_duas" not in data or "evening_duas" not in data:
            results.log_fail("Duas Collection API", "Missing morning_duas or evening_duas field")
            return
            
        # Verify structure
        morning_duas = data["morning_duas"]
        if not isinstance(morning_duas, list) or len(morning_duas) == 0:
            results.log_fail("Duas Collection API", "morning_duas should be non-empty list")
            return
            
        # Check first morning dua structure
        first_dua = morning_duas[0]
        required_fields = ["id", "title_kurdish", "title_arabic", "kurdish", "arabic", "transliteration"]
        for field in required_fields:
            if field not in first_dua:
                results.log_fail("Duas Collection API", f"Missing field '{field}' in morning dua")
                return
                
        results.log_pass("Duas Collection API")
        
    except Exception as e:
        results.log_fail("Duas Collection API", f"Exception: {str(e)}")

def test_quran_verses_regression(results, base_url: str, timeout: float):
    """تاقیکردنەوەی ئەیتەکانی قورئان"""
    print(f"\n📖 تاقیکردنەوەی ئەیتەکانی قورئان...")
    
    try:
        response = get(f"{base_url}/quran", timeout=timeout)
        
        if response.status_code != 200:
            results.log_fail("Quran Verses API", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        if "verses" not in data:
            results.log_fail("Quran Verses API", "Missing verses field")
            return
            
        verses = data["verses"]
        if not isinstance(verses, list) or len(verses) == 0:
            results.log_fail("Quran Verses API", "verses should be non-empty list")
            return
            
        # Check first verse structure
        first_verse = verses[0]
        required_fields = ["id", "surah_number", "verse_number", "arabic", "kurdish", "transliteration", "english"]
        for field in required_fields:
            if field not in first_verse:
                results.log_fail("Quran Verses API", f"Missing field '{field}' in verse")
                return
                
        results.log_pass("Quran Verses API")
        
    except Exception as e:
        results.log_fail("Quran Verses API", f"Exception: {str(e)}")

def test_health_check(results, base_url: str, timeout: float):
    """تاقیکردنەوەی هێلثی سیستەم"""
    print(f"\n❤️ تاقیکردنەوەی هێلث چێک...")
    
    try:
        response = get(f"{base_url}/health", timeout=timeout)
        
        if response.status_code != 200:
            results.log_fail("Health Check", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        if "status" not in data or data["status"] != "healthy":
            results.log_fail("Health Check", "Missing or incorrect status field")
            return
            
        if "message" not in data:
            results.log_fail("Health Check", "Missing message field")
            return
            
        results.log_pass("Health Check")
        
    except Exception as e:
        results.log_fail("Health Check", f"Exception: {str(e)}")

def main():
    """ڕادەستی هەموو تاقیکردنەوەکان بکە بە دیزاینی کۆنسۆڵی تایبەت"""
    parser = argparse.ArgumentParser(description="تاقیکردنەوەی APIی پشتەوە")
    parser.add_argument("--url", default=BACKEND_URL, help="URL ـی پشتەوە (بنەڕەت: %(default)s)")
    parser.add_argument("--timeout", type=float, default=10.0, help="کاتی چاوەڕوانی هەر داواكارییەکە (چرکە)")
    parser.add_argument("--no-color", action="store_true", help="بێ ڕەنگ")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(f"{Color.BOLD}🚀 تاقیکردنەوەی ئەپی ئیسلامی کوردی — پشتەوە{Color.RESET}")
    print(f"پشتەوە: {base_url}")
    print("=" * 60)
    print("🎯 سەرنج: کاتەکانی نوێژ بە 12کاتژمێر و نوێژی ئێستا")
    print("📍 خالە تاقیکردنەکان: هەولێر، بەغدا، سلێمانی، دهۆک")
    print("=" * 60)
    
    results = TestResults()
    results.use_color = not args.no_color
    
    # Priority 1: Enhanced Prayer Times Testing
    test_enhanced_prayer_times_api(results, base_url, args.timeout)
    test_prayer_times_error_handling(results, base_url, args.timeout)
    
    # Priority 2: Regression Testing for other APIs
    test_health_check(results, base_url, args.timeout)
    test_cities_api_regression(results, base_url, args.timeout)
    test_qibla_direction_regression(results, base_url, args.timeout)
    test_duas_collection_regression(results, base_url, args.timeout)
    test_quran_verses_regression(results, base_url, args.timeout)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 هەموو تاقیکردنەوەکان سەرکەوتوو بوون!")
        print("✅ فۆرماتی 12کاتژمێر بە ڕوونکردنەوەی ب.ن/د.ن")
        print("✅ دیاریكردنی نوێژی ئێستا کار دەکات")
        print("✅ هەژماری خۆر و کات وشەییەکان بۆ هەموو شوێنەکان گونجاون")
        print("✅ هیچ ڕیگرێکی دووبارە بوونی نەبوو")
        return 0
    else:
        print(f"\n⚠️ {results.failed} تاقیکردن شکستی هێنا. سەرەوە هەڵەکان بخوێنەوە.")
        return 1

if __name__ == "__main__":
    sys.exit(main())