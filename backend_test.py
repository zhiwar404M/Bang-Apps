#!/usr/bin/env python3
"""
Backend API Tests for Kurdish Islamic App
Tests all backend endpoints systematically
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://page-builder-21.preview.emergentagent.com/api"

# Test coordinates
ERBIL_COORDS = {"lat": 36.1911, "lng": 44.0094}
BAGHDAD_COORDS = {"lat": 33.3152, "lng": 44.3661}

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

def test_health_endpoint(results):
    """Test health check endpoint"""
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

def test_kurdish_cities_endpoint(results):
    """Test Kurdish cities endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/cities/kurdish", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Kurdish Cities API", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        if "cities" not in data:
            results.log_fail("Kurdish Cities API", "Missing cities field")
            return
            
        cities = data["cities"]
        if not isinstance(cities, list) or len(cities) == 0:
            results.log_fail("Kurdish Cities API", "Cities should be non-empty list")
            return
            
        # Check if Kurdish cities are present
        kurdish_city_names = [city.get("name", "") for city in cities]
        expected_kurdish = ["هەولێر", "سلێمانی", "دهۆک"]
        
        found_kurdish = any(name in kurdish_city_names for name in expected_kurdish)
        if not found_kurdish:
            results.log_fail("Kurdish Cities API", f"Expected Kurdish cities not found. Got: {kurdish_city_names}")
            return
            
        # Verify city structure
        for city in cities[:3]:  # Check first 3 cities
            required_fields = ["id", "name", "name_en", "lat", "lng"]
            for field in required_fields:
                if field not in city:
                    results.log_fail("Kurdish Cities API", f"Missing field '{field}' in city data")
                    return
                    
        results.log_pass("Kurdish Cities API")
        
    except Exception as e:
        results.log_fail("Kurdish Cities API", f"Exception: {str(e)}")

def test_arabic_cities_endpoint(results):
    """Test Arabic cities endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/cities/arabic", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Arabic Cities API", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        if "cities" not in data:
            results.log_fail("Arabic Cities API", "Missing cities field")
            return
            
        cities = data["cities"]
        if not isinstance(cities, list) or len(cities) == 0:
            results.log_fail("Arabic Cities API", "Cities should be non-empty list")
            return
            
        # Check if Arabic cities are present
        arabic_city_names = [city.get("name", "") for city in cities]
        expected_arabic = ["بغداد", "البصرة", "الموصل"]
        
        found_arabic = any(name in arabic_city_names for name in expected_arabic)
        if not found_arabic:
            results.log_fail("Arabic Cities API", f"Expected Arabic cities not found. Got: {arabic_city_names}")
            return
            
        # Verify city structure
        for city in cities[:3]:  # Check first 3 cities
            required_fields = ["id", "name", "name_en", "lat", "lng"]
            for field in required_fields:
                if field not in city:
                    results.log_fail("Arabic Cities API", f"Missing field '{field}' in city data")
                    return
                    
        results.log_pass("Arabic Cities API")
        
    except Exception as e:
        results.log_fail("Arabic Cities API", f"Exception: {str(e)}")

def test_prayer_times_endpoint(results):
    """Test prayer times calculation for Erbil and Baghdad"""
    test_cases = [
        ("Erbil", ERBIL_COORDS),
        ("Baghdad", BAGHDAD_COORDS)
    ]
    
    for city_name, coords in test_cases:
        try:
            url = f"{BACKEND_URL}/prayer-times/{coords['lat']}/{coords['lng']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                results.log_fail(f"Prayer Times API ({city_name})", f"Status code {response.status_code}")
                continue
                
            data = response.json()
            
            # Check all required prayer times
            required_times = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
            for prayer in required_times:
                if prayer not in data:
                    results.log_fail(f"Prayer Times API ({city_name})", f"Missing {prayer} time")
                    continue
                    
                # Verify time format (HH:MM)
                time_str = data[prayer]
                try:
                    datetime.strptime(time_str, "%H:%M")
                except ValueError:
                    results.log_fail(f"Prayer Times API ({city_name})", f"Invalid time format for {prayer}: {time_str}")
                    continue
                    
            # Check additional fields
            if "date" not in data:
                results.log_fail(f"Prayer Times API ({city_name})", "Missing date field")
                continue
                
            if "city" not in data:
                results.log_fail(f"Prayer Times API ({city_name})", "Missing city field")
                continue
                
            results.log_pass(f"Prayer Times API ({city_name})")
            
        except Exception as e:
            results.log_fail(f"Prayer Times API ({city_name})", f"Exception: {str(e)}")

def test_qibla_direction_endpoint(results):
    """Test Qibla direction calculation for Erbil and Baghdad"""
    test_cases = [
        ("Erbil", ERBIL_COORDS),
        ("Baghdad", BAGHDAD_COORDS)
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
                
            # Verify coordinates match input
            if abs(data["lat"] - coords["lat"]) > 0.001 or abs(data["lng"] - coords["lng"]) > 0.001:
                results.log_fail(f"Qibla Direction API ({city_name})", "Returned coordinates don't match input")
                continue
                
            results.log_pass(f"Qibla Direction API ({city_name})")
            
        except Exception as e:
            results.log_fail(f"Qibla Direction API ({city_name})", f"Exception: {str(e)}")

def test_duas_endpoint(results):
    """Test duas collection endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/duas", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Duas Collection API", f"Status code {response.status_code}")
            return
            
        data = response.json()
        
        # Check for morning and evening duas
        if "morning_duas" not in data:
            results.log_fail("Duas Collection API", "Missing morning_duas field")
            return
            
        if "evening_duas" not in data:
            results.log_fail("Duas Collection API", "Missing evening_duas field")
            return
            
        # Verify morning duas structure
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
                
        # Verify evening duas structure
        evening_duas = data["evening_duas"]
        if not isinstance(evening_duas, list) or len(evening_duas) == 0:
            results.log_fail("Duas Collection API", "evening_duas should be non-empty list")
            return
            
        results.log_pass("Duas Collection API")
        
    except Exception as e:
        results.log_fail("Duas Collection API", f"Exception: {str(e)}")

def test_quran_endpoint(results):
    """Test Quran verses endpoint"""
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
                
        # Verify surah names are present
        surah_fields = ["surah_name_arabic", "surah_name_kurdish", "surah_name_english"]
        for field in surah_fields:
            if field not in first_verse:
                results.log_fail("Quran Verses API", f"Missing field '{field}' in verse")
                return
                
        results.log_pass("Quran Verses API")
        
    except Exception as e:
        results.log_fail("Quran Verses API", f"Exception: {str(e)}")

def test_invalid_language_endpoint(results):
    """Test invalid language handling"""
    try:
        response = requests.get(f"{BACKEND_URL}/cities/invalid", timeout=10)
        
        if response.status_code != 404:
            results.log_fail("Invalid Language Error Handling", f"Expected 404, got {response.status_code}")
            return
            
        results.log_pass("Invalid Language Error Handling")
        
    except Exception as e:
        results.log_fail("Invalid Language Error Handling", f"Exception: {str(e)}")

def main():
    """Run all backend tests"""
    print("🚀 Starting Kurdish Islamic App Backend API Tests")
    print(f"Testing backend at: {BACKEND_URL}")
    print("="*60)
    
    results = TestResults()
    
    # Run all tests
    test_health_endpoint(results)
    test_kurdish_cities_endpoint(results)
    test_arabic_cities_endpoint(results)
    test_prayer_times_endpoint(results)
    test_qibla_direction_endpoint(results)
    test_duas_endpoint(results)
    test_quran_endpoint(results)
    test_invalid_language_endpoint(results)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 All backend tests passed! APIs are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results.failed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())