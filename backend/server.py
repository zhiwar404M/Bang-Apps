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

def get_quran_surahs():
    """Get complete list of Quran surahs with Kurdish names"""
    return [
        {"number": 1, "name_arabic": "الفاتحة", "name_kurdish": "فاتیحە", "name_english": "Al-Fatihah", "verses_count": 7, "type": "مەکی"},
        {"number": 2, "name_arabic": "البقرة", "name_kurdish": "گای ماکەر", "name_english": "Al-Baqarah", "verses_count": 286, "type": "مەدینی"},
        {"number": 3, "name_arabic": "آل عمران", "name_kurdish": "ڕەچەڵەکی عیمران", "name_english": "Aal-E-Imran", "verses_count": 200, "type": "مەدینی"},
        {"number": 4, "name_arabic": "النساء", "name_kurdish": "ژنان", "name_english": "An-Nisa", "verses_count": 176, "type": "مەدینی"},
        {"number": 5, "name_arabic": "المائدة", "name_kurdish": "خوان", "name_english": "Al-Maidah", "verses_count": 120, "type": "مەدینی"},
        {"number": 6, "name_arabic": "الأنعام", "name_kurdish": "چەڵاکەجاتەکان", "name_english": "Al-An'am", "verses_count": 165, "type": "مەکی"},
        {"number": 7, "name_arabic": "الأعراف", "name_kurdish": "بەرزاییەکان", "name_english": "Al-A'raf", "verses_count": 206, "type": "مەکی"},
        {"number": 8, "name_arabic": "الأنفال", "name_kurdish": "غەنیمەتەکان", "name_english": "Al-Anfal", "verses_count": 75, "type": "مەدینی"},
        {"number": 9, "name_arabic": "التوبة", "name_kurdish": "تۆبە", "name_english": "At-Taubah", "verses_count": 129, "type": "مەدینی"},
        {"number": 10, "name_arabic": "يونس", "name_kurdish": "یونوس", "name_english": "Yunus", "verses_count": 109, "type": "مەکی"},
        {"number": 11, "name_arabic": "هود", "name_kurdish": "هوود", "name_english": "Hud", "verses_count": 123, "type": "مەکی"},
        {"number": 12, "name_arabic": "يوسف", "name_kurdish": "یووسف", "name_english": "Yusuf", "verses_count": 111, "type": "مەکی"},
        {"number": 13, "name_arabic": "الرعد", "name_kurdish": "هەورەترشە", "name_english": "Ar-Ra'd", "verses_count": 43, "type": "مەکی"},
        {"number": 14, "name_arabic": "إبراهيم", "name_kurdish": "ئیبراهیم", "name_english": "Ibrahim", "verses_count": 52, "type": "مەکی"},
        {"number": 15, "name_arabic": "الحجر", "name_kurdish": "حیجر", "name_english": "Al-Hijr", "verses_count": 99, "type": "مەکی"},
        {"number": 16, "name_arabic": "النحل", "name_kurdish": "هەنگ", "name_english": "An-Nahl", "verses_count": 128, "type": "مەکی"},
        {"number": 17, "name_arabic": "الإسراء", "name_kurdish": "شەوگەڕان", "name_english": "Al-Isra", "verses_count": 111, "type": "مەکی"},
        {"number": 18, "name_arabic": "الكهف", "name_kurdish": "کەڤ", "name_english": "Al-Kahf", "verses_count": 110, "type": "مەکی"},
        {"number": 19, "name_arabic": "مريم", "name_kurdish": "مەریەم", "name_english": "Maryam", "verses_count": 98, "type": "مەکی"},
        {"number": 20, "name_arabic": "طه", "name_kurdish": "تاهە", "name_english": "Taha", "verses_count": 135, "type": "مەکی"},
        {"number": 21, "name_arabic": "الأنبياء", "name_kurdish": "پێغەمبەران", "name_english": "Al-Anbiya", "verses_count": 112, "type": "مەکی"},
        {"number": 22, "name_arabic": "الحج", "name_kurdish": "حەج", "name_english": "Al-Hajj", "verses_count": 78, "type": "مەدینی"},
        {"number": 23, "name_arabic": "المؤمنون", "name_kurdish": "بەڕاستبووان", "name_english": "Al-Mu'minun", "verses_count": 118, "type": "مەکی"},
        {"number": 24, "name_arabic": "النور", "name_kurdish": "ڕووناکی", "name_english": "An-Nur", "verses_count": 64, "type": "مەدینی"},
        {"number": 25, "name_arabic": "الفرقان", "name_kurdish": "فورقان", "name_english": "Al-Furqan", "verses_count": 77, "type": "مەکی"},
        {"number": 26, "name_arabic": "الشعراء", "name_kurdish": "شاعیران", "name_english": "Ash-Shu'ara", "verses_count": 227, "type": "مەکی"},
        {"number": 27, "name_arabic": "النمل", "name_kurdish": "مێرولە", "name_english": "An-Naml", "verses_count": 93, "type": "مەکی"},
        {"number": 28, "name_arabic": "القصص", "name_kurdish": "چیرۆکەکان", "name_english": "Al-Qasas", "verses_count": 88, "type": "مەکی"},
        {"number": 29, "name_arabic": "العنكبوت", "name_kurdish": "جاڵجاڵۆکە", "name_english": "Al-Ankabut", "verses_count": 69, "type": "مەکی"},
        {"number": 30, "name_arabic": "الروم", "name_kurdish": "ڕۆمییەکان", "name_english": "Ar-Rum", "verses_count": 60, "type": "مەکی"},
        {"number": 31, "name_arabic": "لقمان", "name_kurdish": "لوقمان", "name_english": "Luqman", "verses_count": 34, "type": "مەکی"},
        {"number": 32, "name_arabic": "السجدة", "name_kurdish": "سوجدە", "name_english": "As-Sajdah", "verses_count": 30, "type": "مەکی"},
        {"number": 33, "name_arabic": "الأحزاب", "name_kurdish": "حیزبەکان", "name_english": "Al-Ahzab", "verses_count": 73, "type": "مەدینی"},
        {"number": 34, "name_arabic": "سبأ", "name_kurdish": "سەبە", "name_english": "Saba", "verses_count": 54, "type": "مەکی"},
        {"number": 35, "name_arabic": "فاطر", "name_kurdish": "بەدیهێنەر", "name_english": "Fatir", "verses_count": 45, "type": "مەکی"},
        {"number": 36, "name_arabic": "يس", "name_kurdish": "یاسین", "name_english": "Ya-Sin", "verses_count": 83, "type": "مەکی"},
        {"number": 37, "name_arabic": "الصافات", "name_kurdish": "ڕیزکراوەکان", "name_english": "As-Saffat", "verses_count": 182, "type": "مەکی"},
        {"number": 38, "name_arabic": "ص", "name_kurdish": "ساد", "name_english": "Sad", "verses_count": 88, "type": "مەکی"},
        {"number": 39, "name_arabic": "الزمر", "name_kurdish": "کۆمەڵەکان", "name_english": "Az-Zumar", "verses_count": 75, "type": "مەکی"},
        {"number": 40, "name_arabic": "غافر", "name_kurdish": "لێخۆشبوو", "name_english": "Ghafir", "verses_count": 85, "type": "مەکی"},
        {"number": 41, "name_arabic": "فصلت", "name_kurdish": "ڕوونکراوەتەوە", "name_english": "Fussilat", "verses_count": 54, "type": "مەکی"},
        {"number": 42, "name_arabic": "الشورى", "name_kurdish": "ڕاوێژ", "name_english": "Ash-Shuraa", "verses_count": 53, "type": "مەکی"},
        {"number": 43, "name_arabic": "الزخرف", "name_kurdish": "زێڕین", "name_english": "Az-Zukhruf", "verses_count": 89, "type": "مەکی"},
        {"number": 44, "name_arabic": "الدخان", "name_kurdish": "دووکەڵ", "name_english": "Ad-Dukhan", "verses_count": 59, "type": "مەکی"},
        {"number": 45, "name_arabic": "الجاثية", "name_kurdish": "چۆک دادانیشتوو", "name_english": "Al-Jathiyah", "verses_count": 37, "type": "مەکی"},
        {"number": 46, "name_arabic": "الأحقاف", "name_kurdish": "لێژاییەکان", "name_english": "Al-Ahqaf", "verses_count": 35, "type": "مەکی"},
        {"number": 47, "name_arabic": "محمد", "name_kurdish": "محەمەد", "name_english": "Muhammad", "verses_count": 38, "type": "مەدینی"},
        {"number": 48, "name_arabic": "الفتح", "name_kurdish": "سەرکەوتن", "name_english": "Al-Fath", "verses_count": 29, "type": "مەدینی"},
        {"number": 49, "name_arabic": "الحجرات", "name_kurdish": "ژوورەکان", "name_english": "Al-Hujurat", "verses_count": 18, "type": "مەدینی"},
        {"number": 50, "name_arabic": "ق", "name_kurdish": "قاف", "name_english": "Qaf", "verses_count": 45, "type": "مەکی"},
        {"number": 51, "name_arabic": "الذاريات", "name_kurdish": "بابەتکەرەکان", "name_english": "Adh-Dhariyat", "verses_count": 60, "type": "مەکی"},
        {"number": 52, "name_arabic": "الطور", "name_kurdish": "شاخ", "name_english": "At-Tur", "verses_count": 49, "type": "مەکی"},
        {"number": 53, "name_arabic": "النجم", "name_kurdish": "ئەستێرە", "name_english": "An-Najm", "verses_count": 62, "type": "مەکی"},
        {"number": 54, "name_arabic": "القمر", "name_kurdish": "مانگ", "name_english": "Al-Qamar", "verses_count": 55, "type": "مەکی"},
        {"number": 55, "name_arabic": "الرحمن", "name_kurdish": "بەخشندە", "name_english": "Ar-Rahman", "verses_count": 78, "type": "مەکی"},
        {"number": 56, "name_arabic": "الواقعة", "name_kurdish": "ڕووداوە", "name_english": "Al-Waqiah", "verses_count": 96, "type": "مەکی"},
        {"number": 57, "name_arabic": "الحديد", "name_kurdish": "ئاسن", "name_english": "Al-Hadid", "verses_count": 29, "type": "مەدینی"},
        {"number": 58, "name_arabic": "المجادلة", "name_kurdish": "گرتووبەجی", "name_english": "Al-Mujadila", "verses_count": 22, "type": "مەدینی"},
        {"number": 59, "name_arabic": "الحشر", "name_kurdish": "کۆکردنەوە", "name_english": "Al-Hashr", "verses_count": 24, "type": "مەدینی"},
        {"number": 60, "name_arabic": "الممتحنة", "name_kurdish": "تاقیکراوە", "name_english": "Al-Mumtahanah", "verses_count": 13, "type": "مەدینی"},
        {"number": 61, "name_arabic": "الصف", "name_kurdish": "ڕیز", "name_english": "As-Saff", "verses_count": 14, "type": "مەدینی"},
        {"number": 62, "name_arabic": "الجمعة", "name_kurdish": "هەینی", "name_english": "Al-Jumu'ah", "verses_count": 11, "type": "مەدینی"},
        {"number": 63, "name_arabic": "المنافقون", "name_kurdish": "دووڕوان", "name_english": "Al-Munafiqun", "verses_count": 11, "type": "مەدینی"},
        {"number": 64, "name_arabic": "التغابن", "name_kurdish": "دووبەرەکی", "name_english": "At-Taghabun", "verses_count": 18, "type": "مەدینی"},
        {"number": 65, "name_arabic": "الطلاق", "name_kurdish": "جیابوونەوە", "name_english": "At-Talaq", "verses_count": 12, "type": "مەدینی"},
        {"number": 66, "name_arabic": "التحريم", "name_kurdish": "قەدەغەکردن", "name_english": "At-Tahrim", "verses_count": 12, "type": "مەدینی"},
        {"number": 67, "name_arabic": "الملك", "name_kurdish": "پاشایەتی", "name_english": "Al-Mulk", "verses_count": 30, "type": "مەکی"},
        {"number": 68, "name_arabic": "القلم", "name_kurdish": "پێنووس", "name_english": "Al-Qalam", "verses_count": 52, "type": "مەکی"},
        {"number": 69, "name_arabic": "الحاقة", "name_kurdish": "ڕاستی", "name_english": "Al-Haqqah", "verses_count": 52, "type": "مەکی"},
        {"number": 70, "name_arabic": "المعارج", "name_kurdish": "پلەکانی بەرزبوونەوە", "name_english": "Al-Ma'arij", "verses_count": 44, "type": "مەکی"},
        {"number": 71, "name_arabic": "نوح", "name_kurdish": "نووح", "name_english": "Nuh", "verses_count": 28, "type": "مەکی"},
        {"number": 72, "name_arabic": "الجن", "name_kurdish": "جن", "name_english": "Al-Jinn", "verses_count": 28, "type": "مەکی"},
        {"number": 73, "name_arabic": "المزمل", "name_kurdish": "پێچراو", "name_english": "Al-Muzzammil", "verses_count": 20, "type": "مەکی"},
        {"number": 74, "name_arabic": "المدثر", "name_kurdish": "سەرپۆشراو", "name_english": "Al-Muddaththir", "verses_count": 56, "type": "مەکی"},
        {"number": 75, "name_arabic": "القيامة", "name_kurdish": "ڕۆژی هەستان", "name_english": "Al-Qiyamah", "verses_count": 40, "type": "مەکی"},
        {"number": 76, "name_arabic": "الإنسان", "name_kurdish": "مرۆڤ", "name_english": "Al-Insan", "verses_count": 31, "type": "مەدینی"},
        {"number": 77, "name_arabic": "المرسلات", "name_kurdish": "ناردراوەکان", "name_english": "Al-Mursalat", "verses_count": 50, "type": "مەکی"},
        {"number": 78, "name_arabic": "النبأ", "name_kurdish": "هەواڵە گەورەکە", "name_english": "An-Naba", "verses_count": 40, "type": "مەکی"},
        {"number": 79, "name_arabic": "النازعات", "name_kurdish": "هەڵکێشەرەکان", "name_english": "An-Nazi'at", "verses_count": 46, "type": "مەکی"},
        {"number": 80, "name_arabic": "عبس", "name_kurdish": "ترشی کرد", "name_english": "Abasa", "verses_count": 42, "type": "مەکی"},
        {"number": 81, "name_arabic": "التكوير", "name_kurdish": "گۆشە چیکردن", "name_english": "At-Takwir", "verses_count": 29, "type": "مەکی"},
        {"number": 82, "name_arabic": "الإنفطار", "name_kurdish": "شەق بوون", "name_english": "Al-Infitar", "verses_count": 19, "type": "مەکی"},
        {"number": 83, "name_arabic": "المطففين", "name_kurdish": "کەماو دەرەکان", "name_english": "Al-Mutaffifin", "verses_count": 36, "type": "مەکی"},
        {"number": 84, "name_arabic": "الإنشقاق", "name_kurdish": "شەق بوون", "name_english": "Al-Inshiqaq", "verses_count": 25, "type": "مەکی"},
        {"number": 85, "name_arabic": "البروج", "name_kurdish": "بوروجەکان", "name_english": "Al-Buruj", "verses_count": 22, "type": "مەکی"},
        {"number": 86, "name_arabic": "الطارق", "name_kurdish": "شەوان هاتوو", "name_english": "At-Tariq", "verses_count": 17, "type": "مەکی"},
        {"number": 87, "name_arabic": "الأعلى", "name_kurdish": "بەرزترین", "name_english": "Al-A'la", "verses_count": 19, "type": "مەکی"},
        {"number": 88, "name_arabic": "الغاشية", "name_kurdish": "داپۆشەر", "name_english": "Al-Ghashiyah", "verses_count": 26, "type": "مەکی"},
        {"number": 89, "name_arabic": "الفجر", "name_kurdish": "بەرەبەیان", "name_english": "Al-Fajr", "verses_count": 30, "type": "مەکی"},
        {"number": 90, "name_arabic": "البلد", "name_kurdish": "شار", "name_english": "Al-Balad", "verses_count": 20, "type": "مەکی"},
        {"number": 91, "name_arabic": "الشمس", "name_kurdish": "خۆر", "name_english": "Ash-Shams", "verses_count": 15, "type": "مەکی"},
        {"number": 92, "name_arabic": "الليل", "name_kurdish": "شەو", "name_english": "Al-Layl", "verses_count": 21, "type": "مەکی"},
        {"number": 93, "name_arabic": "الضحى", "name_kurdish": "چاشت", "name_english": "Ad-Duhaa", "verses_count": 11, "type": "مەکی"},
        {"number": 94, "name_arabic": "الشرح", "name_kurdish": "پان کردنەوە", "name_english": "Ash-Sharh", "verses_count": 8, "type": "مەکی"},
        {"number": 95, "name_arabic": "التين", "name_kurdish": "هەنجیر", "name_english": "At-Tin", "verses_count": 8, "type": "مەکی"},
        {"number": 96, "name_arabic": "العلق", "name_kurdish": "پەیوەندی", "name_english": "Al-Alaq", "verses_count": 19, "type": "مەکی"},
        {"number": 97, "name_arabic": "القدر", "name_kurdish": "قەدر", "name_english": "Al-Qadr", "verses_count": 5, "type": "مەکی"},
        {"number": 98, "name_arabic": "البينة", "name_kurdish": "بەڵگەی ڕوون", "name_english": "Al-Bayyinah", "verses_count": 8, "type": "مەدینی"},
        {"number": 99, "name_arabic": "الزلزلة", "name_kurdish": "بوومەلەرزە", "name_english": "Az-Zalzalah", "verses_count": 8, "type": "مەدینی"},
        {"number": 100, "name_arabic": "العاديات", "name_kurdish": "ڕاکەرەکان", "name_english": "Al-Adiyat", "verses_count": 11, "type": "مەکی"},
        {"number": 101, "name_arabic": "القارعة", "name_kurdish": "کێشەی گەورە", "name_english": "Al-Qari'ah", "verses_count": 11, "type": "مەکی"},
        {"number": 102, "name_arabic": "التكاثر", "name_kurdish": "زۆربوون", "name_english": "At-Takathur", "verses_count": 8, "type": "مەکی"},
        {"number": 103, "name_arabic": "العصر", "name_kurdish": "کات", "name_english": "Al-Asr", "verses_count": 3, "type": "مەکی"},
        {"number": 104, "name_arabic": "الهمزة", "name_kurdish": "قسەلێدەر", "name_english": "Al-Humazah", "verses_count": 9, "type": "مەکی"},
        {"number": 105, "name_arabic": "الفيل", "name_kurdish": "فیل", "name_english": "Al-Fil", "verses_count": 5, "type": "مەکی"},
        {"number": 106, "name_arabic": "قريش", "name_kurdish": "قورەیش", "name_english": "Quraysh", "verses_count": 4, "type": "مەکی"},
        {"number": 107, "name_arabic": "الماعون", "name_kurdish": "یارمەتی", "name_english": "Al-Ma'un", "verses_count": 7, "type": "مەکی"},
        {"number": 108, "name_arabic": "الكوثر", "name_kurdish": "کەوسەر", "name_english": "Al-Kawthar", "verses_count": 3, "type": "مەکی"},
        {"number": 109, "name_arabic": "الكافرون", "name_kurdish": "کافرەکان", "name_english": "Al-Kafirun", "verses_count": 6, "type": "مەکی"},
        {"number": 110, "name_arabic": "النصر", "name_kurdish": "یارمەتی", "name_english": "An-Nasr", "verses_count": 3, "type": "مەدینی"},
        {"number": 111, "name_arabic": "المسد", "name_kurdish": "ڕیسمان", "name_english": "Al-Masad", "verses_count": 5, "type": "مەکی"},
        {"number": 112, "name_arabic": "الإخلاص", "name_kurdish": "خاوێنی", "name_english": "Al-Ikhlas", "verses_count": 4, "type": "مەکی"},
        {"number": 113, "name_arabic": "الفلق", "name_kurdish": "بەرەبەیان", "name_english": "Al-Falaq", "verses_count": 5, "type": "مەکی"},
        {"number": 114, "name_arabic": "الناس", "name_kurdish": "خەڵک", "name_english": "An-Nas", "verses_count": 6, "type": "مەکی"}
    ]

def get_quran_verses_by_surah(surah_number: int):
    """Get verses for specific surah - sample implementation with first few surahs"""
    
    # Sample verses for the most commonly read surahs
    sample_verses = {
        1: [  # Al-Fatihah
            {
                "verse_number": 1,
                "arabic": "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ",
                "kurdish": "بە ناوی خوای بەخشندە و میهرەبان",
                "transliteration": "Bismillahir-Rahmanir-Raheem",
                "english": "In the name of Allah, the Most Gracious, the Most Merciful"
            },
            {
                "verse_number": 2,
                "arabic": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
                "kurdish": "هەموو ستایش بۆ خوای گەورەی جیهانیانە",
                "transliteration": "Alhamdulillahi Rabbil-alameen",
                "english": "All praise is due to Allah, Lord of all the worlds"
            },
            {
                "verse_number": 3,
                "arabic": "الرَّحْمَـٰنِ الرَّحِيمِ",
                "kurdish": "بەخشندە و میهرەبان",
                "transliteration": "Ar-Rahmanir-Raheem",
                "english": "The Most Gracious, the Most Merciful"
            },
            {
                "verse_number": 4,
                "arabic": "مَالِكِ يَوْمِ الدِّينِ",
                "kurdish": "خاوەنی ڕۆژی حیساب",
                "transliteration": "Maliki Yawmid-Deen",
                "english": "Master of the Day of Judgment"
            },
            {
                "verse_number": 5,
                "arabic": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
                "kurdish": "تەنها تۆ دەپەرستین و تەنها لە تۆ داوای یارمەتی دەکەین",
                "transliteration": "Iyyaka na'budu wa iyyaka nasta'een",
                "english": "You alone we worship and You alone we ask for help"
            },
            {
                "verse_number": 6,
                "arabic": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
                "kurdish": "ئێمە بەرەو ڕێچکەی ڕاست بەرێ",
                "transliteration": "Ihdinaas-Siraatal-Mustaqeem",
                "english": "Guide us to the straight path"
            },
            {
                "verse_number": 7,
                "arabic": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
                "kurdish": "ڕێچکەی ئەوانەی تۆ نیعمەتت پێدان، نەک ئەوانەی تووڕەیی لێکراون و نە گومڕاوەکان",
                "transliteration": "Siraatal-lazeena an'amta 'alayhim ghayril-maghdoobi 'alayhim wa lad-daaalleen",
                "english": "The path of those You have blessed, not of those who have incurred Your wrath, nor of those who have gone astray"
            }
        ],
        2: [  # Al-Baqarah (first few verses)
            {
                "verse_number": 1,
                "arabic": "الم",
                "kurdish": "ئەلیف لام میم",
                "transliteration": "Alif Lam Meem",
                "english": "Alif, Lam, Meem"
            },
            {
                "verse_number": 2,
                "arabic": "ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِّلْمُتَّقِينَ",
                "kurdish": "ئەم کتابە کە هیچ گومانی تێدا نییە، ڕێنمایی بۆ پارێزگارانە",
                "transliteration": "Zalikal-kitabu la rayba feeh, hudan lil-muttaqeen",
                "english": "This is the Book about which there is no doubt, a guidance for those conscious of Allah"
            },
            {
                "verse_number": 3,
                "arabic": "الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ",
                "kurdish": "ئەوانەی باوەڕیان بە نادیار هەیە و نوێژ دەکەن و لەوەی ڕۆزیمان پێداون خەرج دەکەن",
                "transliteration": "Allazeena yu'minoona bil-ghaybi wa yuqeemoonas-salaata wa mimma razaqnaahum yunfiqoon",
                "english": "Who believe in the unseen, establish prayer, and spend out of what We have provided for them"
            }
        ],
        3: [  # Aal-E-Imran (first few verses)
            {
                "verse_number": 1,
                "arabic": "الم",
                "kurdish": "ئەلیف لام میم",
                "transliteration": "Alif Lam Meem",
                "english": "Alif, Lam, Meem"
            },
            {
                "verse_number": 2,
                "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
                "kurdish": "خوا، هیچ خودایەک نییە جگە لە ئەو، زیندووی هەمیشە زیندووە",
                "transliteration": "Allahu la ilaha illa huwal-hayyul-qayyoom",
                "english": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence"
            }
        ],
        112: [  # Al-Ikhlas
            {
                "verse_number": 1,
                "arabic": "قُلْ هُوَ اللَّهُ أَحَدٌ",
                "kurdish": "بڵێ: ئەو خوایە یەکتایە",
                "transliteration": "Qul huwa Allahu ahad",
                "english": "Say: He is Allah, the One"
            },
            {
                "verse_number": 2,
                "arabic": "اللَّهُ الصَّمَدُ",
                "kurdish": "خوا بێ پێویستە",
                "transliteration": "Allahus-samad",
                "english": "Allah, the Eternal, Absolute"
            },
            {
                "verse_number": 3,
                "arabic": "لَمْ يَلِدْ وَلَمْ يُولَدْ",
                "kurdish": "نە منداڵی هەیە و نە خۆی منداڵی کەسێکە",
                "transliteration": "Lam yalid wa lam yoolad",
                "english": "He begets not, nor is He begotten"
            },
            {
                "verse_number": 4,
                "arabic": "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
                "kurdish": "و کەس نییە کە وەک ئەو بێت",
                "transliteration": "Wa lam yakun lahu kufuwan ahad",
                "english": "And there is none like unto Him"
            }
        ],
        113: [  # Al-Falaq
            {
                "verse_number": 1,
                "arabic": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
                "kurdish": "بڵێ: پەنا دەبەمە بەر خوای بەرەبەیان",
                "transliteration": "Qul a'oozu bi rabbil-falaq",
                "english": "Say: I seek refuge in the Lord of daybreak"
            },
            {
                "verse_number": 2,
                "arabic": "مِن شَرِّ مَا خَلَقَ",
                "kurdish": "لە خراپەی ئەوەی دروستی کردووە",
                "transliteration": "Min sharri ma khalaq",
                "english": "From the evil of that which He created"
            }
        ],
        114: [  # An-Nas
            {
                "verse_number": 1,
                "arabic": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
                "kurdish": "بڵێ: پەنا دەبەمە بەر خوای خەڵک",
                "transliteration": "Qul a'oozu bi rabbin-nas",
                "english": "Say: I seek refuge in the Lord of mankind"
            },
            {
                "verse_number": 2,
                "arabic": "مَلِكِ النَّاسِ",
                "kurdish": "پاشای خەڵک",
                "transliteration": "Malikin-nas",
                "english": "The Sovereign of mankind"
            }
        ]
    }
    
    return sample_verses.get(surah_number, [])

def get_app_settings(user_id: str = "default"):
    """Get default app settings"""
    return {
        "user_id": user_id,
        "theme": "default",
        "font_size": "medium",
        "arabic_font": "amiri",
        "language": "kurdish",
        "prayer_notifications": True,
        "auto_location": False,
        "quran_translation": True,
        "verse_numbers": True,
        "prayer_sound": True,
        "24_hour_format": False,
        "hijri_calendar": True,
        "default_city": None,
        "notification_times": {
            "fajr": True,
            "dhuhr": True,
            "asr": True,
            "maghrib": True,
            "isha": True
        }
    }

def update_app_settings(user_id: str, settings: dict):
    """Update app settings for a user"""
    # In a real app, this would save to database
    # For now, we'll just return the updated settings
    default_settings = get_app_settings(user_id)
    default_settings.update(settings)
    return default_settings

def get_surah_info(surah_number: int):
    """Get detailed information about a specific surah"""
    surahs = get_quran_surahs()
    surah = next((s for s in surahs if s["number"] == surah_number), None)
    if not surah:
        return None
    
    verses = get_quran_verses_by_surah(surah_number)
    
    return {
        "surah_info": surah,
        "verses": verses,
        "total_verses": len(verses) if verses else surah["verses_count"]
    }

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

@app.get("/api/quran/surahs")
async def get_surahs():
    """Get list of all Quran surahs"""
    try:
        surahs = get_quran_surahs()
        return {"surahs": surahs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quran/surah/{surah_number}")
async def get_surah(surah_number: int):
    """Get specific surah with verses"""
    try:
        if surah_number < 1 or surah_number > 114:
            raise HTTPException(status_code=400, detail="Invalid surah number")
        
        surah_data = get_surah_info(surah_number)
        if not surah_data:
            raise HTTPException(status_code=404, detail="Surah not found")
        
        return surah_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_settings(user_id: str = "default"):
    """Get user settings"""
    try:
        settings = get_app_settings(user_id)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings")
async def update_settings(settings: dict, user_id: str = "default"):
    """Update user settings"""
    try:
        updated_settings = update_app_settings(user_id, settings)
        return updated_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Kurdish Islamic App API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)