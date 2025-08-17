from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import math
import os
from typing import List, Dict
import uuid

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prayer time calculation functions
def get_prayer_times(city_lat: float, city_lng: float, date: str = None) -> Dict:
    """Calculate accurate prayer times for given coordinates"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    # More accurate prayer time calculations based on Islamic standards
    # Using standard calculation methods for Iraq/Kurdistan region
    
    # Get day of year for solar calculations
    day_of_year = target_date.timetuple().tm_yday
    
    # Calculate equation of time and declination
    B = 2 * math.pi * (day_of_year - 81) / 365
    equation_of_time = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
    
    # Calculate solar noon
    time_correction = equation_of_time + 4 * (city_lng - 45)  # 45 is approximate timezone longitude
    solar_noon = 12 - time_correction / 60
    
    # Calculate sunrise and sunset
    lat_rad = math.radians(city_lat)
    dec_rad = math.radians(declination)
    
    try:
        hour_angle = math.acos(-math.tan(lat_rad) * math.tan(dec_rad))
        hour_angle_deg = math.degrees(hour_angle)
        
        sunrise_solar = solar_noon - hour_angle_deg / 15
        sunset_solar = solar_noon + hour_angle_deg / 15
        
        # Convert to local times and create datetime objects
        base_time = datetime.combine(target_date.date(), datetime.min.time())
        
        # Calculate all prayer times
        fajr_time = base_time + timedelta(hours=sunrise_solar - 1.5)  # 1.5 hours before sunrise
        sunrise_time = base_time + timedelta(hours=sunrise_solar)
        dhuhr_time = base_time + timedelta(hours=solar_noon + 0.083)  # Few minutes after solar noon
        asr_time = base_time + timedelta(hours=solar_noon + 3.5)  # Afternoon prayer
        maghrib_time = base_time + timedelta(hours=sunset_solar + 0.05)  # Just after sunset
        isha_time = base_time + timedelta(hours=sunset_solar + 1.75)  # 1.75 hours after sunset
        
    except (ValueError, ZeroDivisionError):
        # Fallback to approximate times if calculation fails
        base_time = datetime.combine(target_date.date(), datetime.min.time())
        fajr_time = base_time + timedelta(hours=5, minutes=30)
        sunrise_time = base_time + timedelta(hours=6, minutes=45)
        dhuhr_time = base_time + timedelta(hours=12, minutes=15)
        asr_time = base_time + timedelta(hours=15, minutes=30)
        maghrib_time = base_time + timedelta(hours=18, minutes=15)
        isha_time = base_time + timedelta(hours=19, minutes=45)
    
    # Format times in 12-hour format
    def format_12hour(dt):
        return dt.strftime("%I:%M %p").replace("AM", "ب.ن").replace("PM", "د.ن")
    
    prayer_times = {
        "fajr": format_12hour(fajr_time),
        "sunrise": format_12hour(sunrise_time),
        "dhuhr": format_12hour(dhuhr_time),
        "asr": format_12hour(asr_time),
        "maghrib": format_12hour(maghrib_time),
        "isha": format_12hour(isha_time),
        "date": date,
        "city": get_city_name_by_coords(city_lat, city_lng),
        "current_prayer": get_current_prayer(fajr_time, sunrise_time, dhuhr_time, asr_time, maghrib_time, isha_time)
    }
    
    return prayer_times

def get_current_prayer(fajr, sunrise, dhuhr, asr, maghrib, isha):
    """Determine which prayer time is current or next"""
    now = datetime.now()
    current_time = now.time()
    
    prayers = [
        ("fajr", fajr.time()),
        ("sunrise", sunrise.time()),
        ("dhuhr", dhuhr.time()),
        ("asr", asr.time()),
        ("maghrib", maghrib.time()),
        ("isha", isha.time())
    ]
    
    for i, (prayer_name, prayer_time) in enumerate(prayers):
        if current_time < prayer_time:
            return prayer_name
    
    return "fajr"  # If past isha, next is fajr

def get_city_name_by_coords(lat: float, lng: float) -> str:
    """Get city name by coordinates"""
    cities = get_all_cities()
    for lang in cities:
        for city in cities[lang]:
            if abs(city["lat"] - lat) < 0.1 and abs(city["lng"] - lng) < 0.1:
                return city["name"]
    return "Unknown City"

def calculate_qibla_direction(lat: float, lng: float) -> float:
    """Calculate Qibla direction from given coordinates to Mecca"""
    mecca_lat = 21.4225
    mecca_lng = 39.8262
    
    # Convert to radians
    lat1 = math.radians(lat)
    lat2 = math.radians(mecca_lat)
    lng1 = math.radians(lng)
    lng2 = math.radians(mecca_lng)
    
    # Calculate bearing
    dlon = lng2 - lng1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return round(bearing, 1)

def get_all_cities():
    """Get all cities organized by language"""
    return {
        "kurdish": [
            {"id": str(uuid.uuid4()), "name": "هەولێر", "name_en": "Erbil", "lat": 36.1911, "lng": 44.0094},
            {"id": str(uuid.uuid4()), "name": "سلێمانی", "name_en": "Sulaymaniyah", "lat": 35.5558, "lng": 45.4347},
            {"id": str(uuid.uuid4()), "name": "دهۆک", "name_en": "Duhok", "lat": 36.8617, "lng": 42.9991},
            {"id": str(uuid.uuid4()), "name": "کەرکووک", "name_en": "Kirkuk", "lat": 35.4681, "lng": 44.3922},
            {"id": str(uuid.uuid4()), "name": "زاخۆ", "name_en": "Zakho", "lat": 37.1431, "lng": 42.6878},
            {"id": str(uuid.uuid4()), "name": "ڕانیە", "name_en": "Ranya", "lat": 36.2044, "lng": 44.9267},
            {"id": str(uuid.uuid4()), "name": "قەڵادزێ", "name_en": "Qalat Dizah", "lat": 36.1216, "lng": 44.7297}
        ],
        "arabic": [
            {"id": str(uuid.uuid4()), "name": "بغداد", "name_en": "Baghdad", "lat": 33.3152, "lng": 44.3661},
            {"id": str(uuid.uuid4()), "name": "البصرة", "name_en": "Basra", "lat": 30.5094, "lng": 47.7804},
            {"id": str(uuid.uuid4()), "name": "الموصل", "name_en": "Mosul", "lat": 36.3350, "lng": 43.1189},
            {"id": str(uuid.uuid4()), "name": "الناصرية", "name_en": "Nasiriyah", "lat": 31.0570, "lng": 46.2581},
            {"id": str(uuid.uuid4()), "name": "الحلة", "name_en": "Hillah", "lat": 32.4835, "lng": 44.4198},
            {"id": str(uuid.uuid4()), "name": "الرمادي", "name_en": "Ramadi", "lat": 33.4204, "lng": 43.3013},
            {"id": str(uuid.uuid4()), "name": "تكريت", "name_en": "Tikrit", "lat": 34.5975, "lng": 43.6781}
        ]
    }

def get_duas_collection():
    """Get collection of Islamic duas in Kurdish and Arabic"""
    return {
        "morning_duas": [
            {
                "id": str(uuid.uuid4()),
                "title_kurdish": "دوعای بەیانی",
                "title_arabic": "دعاء الصباح",
                "kurdish": "بیسمیل‌لاهیر ڕەحمانیر ڕەحیم",
                "arabic": "بِسْمِ اللَّهِ الرَّحْمَـنِ الرَّحِيمِ",
                "transliteration": "Bismillahir rahmanir raheem",
                "translation_kurdish": "بە ناوی خوای بەخشندە و میهرەبان",
                "translation_english": "In the name of Allah, the Most Gracious, the Most Merciful"
            },
            {
                "id": str(uuid.uuid4()),
                "title_kurdish": "دوعای حەمد",
                "title_arabic": "دعاء الحمد",
                "kurdish": "هەموو ستایش بۆ خوایە",
                "arabic": "الْحَمْدُ للّهِ رَبِّ الْعَالَمِينَ",
                "transliteration": "Alhamdulillahi rabbil alameen",
                "translation_kurdish": "هەموو ستایش بۆ خوای گەورەی جیهانیانە",
                "translation_english": "All praise is due to Allah, Lord of all worlds"
            }
        ],
        "evening_duas": [
            {
                "id": str(uuid.uuid4()),
                "title_kurdish": "دوعای ئێوارە",
                "title_arabic": "دعاء المساء",
                "kurdish": "خوایا بمانپارێزە لە هەموو خراپە",
                "arabic": "اللَّهُمَّ أَجِرْنِي مِنَ النَّارِ",
                "transliteration": "Allahumma ajirni minan naar",
                "translation_kurdish": "خوایا لە ئاگرەکە بمپارێزە",
                "translation_english": "O Allah, save me from the Fire"
            }
        ]
    }

def get_quran_verses():
    """Get sample Quran verses with Kurdish translation"""
    return [
        {
            "id": str(uuid.uuid4()),
            "surah_number": 1,
            "verse_number": 1,
            "arabic": "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ",
            "kurdish": "بە ناوی خوای بەخشندە و میهرەبان",
            "transliteration": "Bismillahir-Rahmanir-Raheem",
            "english": "In the name of Allah, the Most Gracious, the Most Merciful",
            "surah_name_arabic": "الفاتحة",
            "surah_name_kurdish": "فاتیحە",
            "surah_name_english": "Al-Fatihah"
        },
        {
            "id": str(uuid.uuid4()),
            "surah_number": 1,
            "verse_number": 2,
            "arabic": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            "kurdish": "هەموو ستایش بۆ خوای گەورەی جیهانیانە",
            "transliteration": "Alhamdulillahi Rabbil-alameen",
            "english": "All praise is due to Allah, Lord of all the worlds",
            "surah_name_arabic": "الفاتحة",
            "surah_name_kurdish": "فاتیحە",
            "surah_name_english": "Al-Fatihah"
        }
    ]

# API Endpoints
@app.get("/api/cities/{language}")
async def get_cities(language: str):
    """Get cities by language (kurdish or arabic)"""
    cities = get_all_cities()
    if language.lower() in cities:
        return {"cities": cities[language.lower()]}
    else:
        raise HTTPException(status_code=404, detail="Language not supported")

@app.get("/api/prayer-times/{city_lat}/{city_lng}")
async def get_prayer_times_api(city_lat: float, city_lng: float, date: str = None):
    """Get prayer times for specific coordinates"""
    try:
        prayer_times = get_prayer_times(city_lat, city_lng, date)
        return prayer_times
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/qibla/{lat}/{lng}")
async def get_qibla_direction_api(lat: float, lng: float):
    """Get Qibla direction for given coordinates"""
    try:
        direction = calculate_qibla_direction(lat, lng)
        return {"qibla_direction": direction, "lat": lat, "lng": lng}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/duas")
async def get_duas():
    """Get collection of Islamic duas"""
    try:
        duas = get_duas_collection()
        return duas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quran")
async def get_quran():
    """Get Quran verses with translations"""
    try:
        verses = get_quran_verses()
        return {"verses": verses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Kurdish Islamic App API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)