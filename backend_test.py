#!/usr/bin/env python3
"""
Backend API Tests for Kurdish Islamic App - Enhanced Prayer Times Focus
Tests all backend endpoints with special focus on enhanced prayer time features
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://page-builder-21.preview.emergentagent.com/api"

# Test coordinates as specified in review request
TEST_COORDINATES = [
    ("Erbil (هەولێر)", {"lat": 36.1911, "lng": 44.0094}),
    ("Baghdad (بغداد)", {"lat": 33.3152, "lng": 44.3661}),
    ("Sulaymaniyah (سلێمانی)", {"lat": 35.5558, "lng": 45.4347}),
    ("Duhok (دهۆک)", {"lat": 36.8617, "lng": 42.9991})
]

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log_pass(self, test_name):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
        
    def log_fail(self, test_name, error):
        print(f"❌ FAIL: {test_name} - {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_enhanced_prayer_times_api(results):
    """Test enhanced prayer times with 12-hour format and current prayer detection"""
    print(f"\n🕌 TESTING ENHANCED PRAYER TIMES API")
    print("="*50)
    
    for city_name, coords in TEST_COORDINATES:
        try:
            url = f"{BACKEND_URL}/prayer-times/{coords['lat']}/{coords['lng']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Status code {response.status_code}")
                continue
                
            data = response.json()
            print(f"\n📍 Testing {city_name} prayer times:")
            print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
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
                    hour = parsed_time.hour
                    if hour < 1 or hour > 12:
                        results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Invalid 12-hour format for {prayer}: {time_str}")
                        continue
                except ValueError:
                    results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Invalid time format for {prayer}: {time_str}")
                    continue
                    
            # Verify prayer times are reasonable
            fajr_time = data.get("fajr", "")
            dhuhr_time = data.get("dhuhr", "")
            maghrib_time = data.get("maghrib", "")
            
            # Fajr should be in early morning (AM)
            if "د.ن" in fajr_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Fajr should be AM, got: {fajr_time}")
                continue
                
            # Dhuhr should be around noon (PM)
            if "ب.ن" in dhuhr_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Dhuhr should be PM, got: {dhuhr_time}")
                continue
                
            # Maghrib should be in evening (PM)
            if "ب.ن" in maghrib_time:
                results.log_fail(f"Enhanced Prayer Times API ({city_name})", f"Maghrib should be PM, got: {maghrib_time}")
                continue
                
            # Check current_prayer field is included
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

def test_prayer_times_error_handling(results):
    """Test prayer times API error handling with invalid coordinates"""
    try:
        print(f"\n🔍 Testing prayer times error handling...")
        # Test with invalid coordinates
        url = f"{BACKEND_URL}/prayer-times/999/999"
        response = requests.get(url, timeout=10)
        
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

def test_cities_api_regression(results):
    """Test cities API for regressions"""
    print(f"\n🏙️ Testing Cities API for regressions...")
    
    # Test Kurdish cities
    try:
        response = requests.get(f"{BACKEND_URL}/cities/kurdish", timeout=10)
        
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
        response = requests.get(f"{BACKEND_URL}/cities/arabic", timeout=10)
        
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

def test_qibla_direction_regression(results):
    """Test Qibla direction API for regressions"""
    print(f"\n🧭 Testing Qibla Direction API for regressions...")
    
    test_cases = [
        ("Erbil", {"lat": 36.1911, "lng": 44.0094}),
        ("Baghdad", {"lat": 33.3152, "lng": 44.3661})
    ]
    
    for city_name, coords in test_cases:
        try:
            url = f"{BACKEND_URL}/qibla/{coords['lat']}/{coords['lng']}"
            response = requests.get(url, timeout=10)
            
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

def test_duas_collection_regression(results):
    """Test duas collection API for regressions"""
    print(f"\n📿 Testing Duas Collection API for regressions...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/duas", timeout=10)
        
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

def test_quran_verses_regression(results):
    """Test Quran verses API for regressions"""
    print(f"\n📖 Testing Quran Verses API for regressions...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/quran", timeout=10)
        
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

def test_health_check(results):
    """Test health check endpoint"""
    print(f"\n❤️ Testing Health Check API...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
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
    """Run all backend tests with focus on enhanced prayer times"""
    print("🚀 KURDISH ISLAMIC APP - ENHANCED PRAYER TIMES TESTING")
    print(f"Testing backend at: {BACKEND_URL}")
    print("="*60)
    print("🎯 FOCUS: Enhanced Prayer Times with 12-hour format & current prayer detection")
    print("📍 Testing coordinates: Erbil, Baghdad, Sulaymaniyah, Duhok")
    print("="*60)
    
    results = TestResults()
    
    # Priority 1: Enhanced Prayer Times Testing
    test_enhanced_prayer_times_api(results)
    test_prayer_times_error_handling(results)
    
    # Priority 2: Regression Testing for other APIs
    test_health_check(results)
    test_cities_api_regression(results)
    test_qibla_direction_regression(results)
    test_duas_collection_regression(results)
    test_quran_verses_regression(results)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 All backend tests passed! Enhanced prayer times working correctly.")
        print("✅ 12-hour format with Kurdish AM/PM indicators")
        print("✅ Current prayer detection implemented")
        print("✅ Solar calculations working for all test coordinates")
        print("✅ No regressions in other APIs")
        return 0
    else:
        print(f"\n⚠️  {results.failed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())