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
    """Calculate prayer times for given coordinates"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Simplified prayer time calculation (using basic astronomical formulas)
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    # Basic calculation - this is simplified, in real app would use proper Islamic prayer time library
    sunrise_time = datetime.combine(target_date.date(), datetime.min.time()) + timedelta(hours=6)
    
    prayer_times = {
        "fajr": (sunrise_time - timedelta(hours=1, minutes=30)).strftime("%H:%M"),
        "sunrise": sunrise_time.strftime("%H:%M"),
        "dhuhr": (sunrise_time + timedelta(hours=6)).strftime("%H:%M"),
        "asr": (sunrise_time + timedelta(hours=9)).strftime("%H:%M"),
        "maghrib": (sunrise_time + timedelta(hours=12)).strftime("%H:%M"),
        "isha": (sunrise_time + timedelta(hours=13, minutes=30)).strftime("%H:%M"),
        "date": date,
        "city": get_city_name_by_coords(city_lat, city_lng)
    }
    
    return prayer_times

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