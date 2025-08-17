import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [language, setLanguage] = useState('kurdish');
  const [activeTab, setActiveTab] = useState('prayer-times');
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [prayerTimes, setPrayerTimes] = useState(null);
  const [qiblaDirection, setQiblaDirection] = useState(null);
  const [duas, setDuas] = useState(null);
  const [quranSurahs, setQuranSurahs] = useState([]);
  const [selectedSurah, setSelectedSurah] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  const translations = {
    kurdish: {
      title: 'ئەپی ئیسلامی کوردی',
      prayerTimes: 'کاتەکانی نوێژ',
      qibla: 'قیبلە',
      duas: 'دوعاکان',
      quran: 'قورئان',
      settings: 'ڕێکخستنەکان',
      selectCity: 'شارەکە هەڵبژێرە',
      selectSurah: 'سورەتەکە هەڵبژێرە',
      fajr: 'بەیانی',
      sunrise: 'خۆرهەڵات',
      dhuhr: 'نیوەڕۆ',
      asr: 'عەسر',
      maghrib: 'مەغرب',
      isha: 'عەتمە',
      qiblaDirection: 'ئاراستەی قیبلە',
      morningDuas: 'دوعای بەیانی',
      eveningDuas: 'دوعای ئێوارە',
      loading: 'چاوەڕێ بکە...',
      generalSettings: 'ڕێکخستنی گشتی',
      displaySettings: 'ڕێکخستنی پیشاندان',
      notificationSettings: 'ڕێکخستنی ئاگادارکردنەوە',
      theme: 'ڕووکار',
      fontSize: 'قەبارەی فۆنت',
      arabicFont: 'فۆنتی عەرەبی',
      prayerNotifications: 'ئاگادارکردنەوەی نوێژ',
      prayerSound: 'دەنگی نوێژ',
      hijriCalendar: 'ڕۆژژمێری کۆچی',
      save: 'پاشەکەوتکردن',
      cancel: 'هەڵوەشاندنەوە',
      verses: 'ئایەت',
      surahInfo: 'زانیاری سورەت'
    },
    arabic: {
      title: 'التطبيق الإسلامي العربي',
      prayerTimes: 'أوقات الصلاة',
      qibla: 'القبلة',
      duas: 'الأدعية',
      quran: 'القرآن',
      settings: 'الإعدادات',
      selectCity: 'اختر المدينة',
      selectSurah: 'اختر السورة',
      fajr: 'الفجر',
      sunrise: 'الشروق',
      dhuhr: 'الظهر',
      asr: 'العصر',
      maghrib: 'المغرب',
      isha: 'العشاء',
      qiblaDirection: 'اتجاه القبلة',
      morningDuas: 'أدعية الصباح',
      eveningDuas: 'أدعية المساء',
      loading: 'جاري التحميل...',
      generalSettings: 'الإعدادات العامة',
      displaySettings: 'إعدادات العرض',
      notificationSettings: 'إعدادات التنبيهات',
      theme: 'المظهر',
      fontSize: 'حجم الخط',
      arabicFont: 'الخط العربي',
      prayerNotifications: 'تنبيهات الصلاة',
      prayerSound: 'صوت الصلاة',
      hijriCalendar: 'التقويم الهجري',
      save: 'حفظ',
      cancel: 'إلغاء',
      verses: 'آيات',
      surahInfo: 'معلومات السورة'
    }
  };

  const currentLang = translations[language];

  useEffect(() => {
    fetchCities();
    fetchDuas();
    fetchQuranSurahs();
    fetchSettings();
  }, [language]);

  const fetchCities = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/cities/${language}`);
      const data = await response.json();
      setCities(data.cities || []);
      setSelectedCity(null);
      setPrayerTimes(null);
      setQiblaDirection(null);
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  const fetchPrayerTimes = async (city) => {
    if (!city) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/prayer-times/${city.lat}/${city.lng}`);
      const data = await response.json();
      setPrayerTimes(data);
    } catch (error) {
      console.error('Error fetching prayer times:', error);
    }
    setLoading(false);
  };

  const fetchQiblaDirection = async (city) => {
    if (!city) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/qibla/${city.lat}/${city.lng}`);
      const data = await response.json();
      setQiblaDirection(data);
    } catch (error) {
      console.error('Error fetching qibla direction:', error);
    }
    setLoading(false);
  };

  const fetchDuas = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/duas`);
      const data = await response.json();
      setDuas(data);
    } catch (error) {
      console.error('Error fetching duas:', error);
    }
  };

  const fetchQuranVerses = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/quran`);
      const data = await response.json();
      setQuranVerses(data.verses || []);
    } catch (error) {
      console.error('Error fetching quran verses:', error);
    }
  };

  const fetchQuranSurahs = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/quran/surahs`);
      const data = await response.json();
      setQuranSurahs(data.surahs || []);
    } catch (error) {
      console.error('Error fetching quran surahs:', error);
    }
  };

  const fetchSurah = async (surahNumber) => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/quran/surah/${surahNumber}`);
      const data = await response.json();
      setSelectedSurah(data);
    } catch (error) {
      console.error('Error fetching surah:', error);
    }
    setLoading(false);
  };

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const updateSettings = async (newSettings) => {
    try {
      const response = await fetch(`${backendUrl}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      });
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error updating settings:', error);
    }
  };

  const handleCityChange = (event) => {
    const cityId = event.target.value;
    const city = cities.find(c => c.id === cityId);
    setSelectedCity(city);
    
    if (activeTab === 'prayer-times') {
      fetchPrayerTimes(city);
    } else if (activeTab === 'qibla') {
      fetchQiblaDirection(city);
    }
  };

  const handleSurahChange = (event) => {
    const surahNumber = parseInt(event.target.value);
    if (surahNumber) {
      fetchSurah(surahNumber);
    } else {
      setSelectedSurah(null);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    if (selectedCity) {
      if (tab === 'prayer-times') {
        fetchPrayerTimes(selectedCity);
      } else if (tab === 'qibla') {
        fetchQiblaDirection(selectedCity);
      }
    }
  };

  const renderPrayerTimes = () => {
    if (!selectedCity) {
      return (
        <div className="text-center py-8 text-gray-600">
          <div className="mb-4 text-6xl">🕌</div>
          <p className="text-lg">{currentLang.selectCity}</p>
        </div>
      );
    }

    if (loading) {
      return (
        <div className="text-center py-8">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">{currentLang.loading}</p>
        </div>
      );
    }

    if (!prayerTimes) {
      return (
        <div className="text-center py-8 text-gray-600">
          <div className="spinner mx-auto mb-4"></div>
          <p>{currentLang.loading}</p>
        </div>
      );
    }

    const prayers = [
      { 
        name: currentLang.fajr, 
        time: prayerTimes.fajr, 
        icon: '🌅',
        color: 'from-indigo-500 to-purple-600',
        borderColor: 'border-indigo-500',
        bgColor: 'bg-indigo-50',
        isCurrent: prayerTimes.current_prayer === 'fajr'
      },
      { 
        name: currentLang.sunrise, 
        time: prayerTimes.sunrise, 
        icon: '☀️',
        color: 'from-yellow-500 to-orange-500',
        borderColor: 'border-yellow-500',
        bgColor: 'bg-yellow-50',
        isCurrent: prayerTimes.current_prayer === 'sunrise'
      },
      { 
        name: currentLang.dhuhr, 
        time: prayerTimes.dhuhr, 
        icon: '🌞',
        color: 'from-orange-500 to-red-500',
        borderColor: 'border-orange-500',
        bgColor: 'bg-orange-50',
        isCurrent: prayerTimes.current_prayer === 'dhuhr'
      },
      { 
        name: currentLang.asr, 
        time: prayerTimes.asr, 
        icon: '🌤️',
        color: 'from-amber-500 to-yellow-600',
        borderColor: 'border-amber-500',
        bgColor: 'bg-amber-50',
        isCurrent: prayerTimes.current_prayer === 'asr'
      },
      { 
        name: currentLang.maghrib, 
        time: prayerTimes.maghrib, 
        icon: '🌇',
        color: 'from-red-500 to-pink-600',
        borderColor: 'border-red-500',
        bgColor: 'bg-red-50',
        isCurrent: prayerTimes.current_prayer === 'maghrib'
      },
      { 
        name: currentLang.isha, 
        time: prayerTimes.isha, 
        icon: '🌙',
        color: 'from-blue-600 to-indigo-700',
        borderColor: 'border-blue-600',
        bgColor: 'bg-blue-50',
        isCurrent: prayerTimes.current_prayer === 'isha'
      }
    ];

    return (
      <div className="space-y-6">
        {/* Header Section */}
        <div className="text-center bg-gradient-to-r from-green-600 to-emerald-700 text-white rounded-2xl p-6 shadow-lg">
          <div className="mb-3">
            <h3 className="text-2xl font-bold mb-2">🕌 {selectedCity.name}</h3>
            <p className="text-green-100 text-lg">{new Date().toLocaleDateString('ar-SA')}</p>
          </div>
          <div className="text-sm text-green-200">
            {language === 'kurdish' ? 'کاتەکانی نوێژ بۆ ئەمڕۆ' : 'أوقات الصلاة اليوم'}
          </div>
        </div>

        {/* Prayer Times Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prayers.map((prayer, index) => (
            <div 
              key={index} 
              className={`
                relative overflow-hidden rounded-2xl shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl
                ${prayer.isCurrent ? 'ring-4 ring-green-400 scale-105 animate-pulse-soft' : ''}
                ${prayer.bgColor} border-2 ${prayer.borderColor}
              `}
            >
              {/* Background Gradient */}
              <div className={`absolute inset-0 bg-gradient-to-br ${prayer.color} opacity-5`}></div>
              
              {/* Current Prayer Indicator */}
              {prayer.isCurrent && (
                <div className="absolute top-0 right-0 bg-green-500 text-white px-3 py-1 rounded-bl-2xl text-xs font-bold">
                  {language === 'kurdish' ? 'ئێستا' : 'الآن'}
                </div>
              )}
              
              {/* Prayer Content */}
              <div className="relative p-6 text-center">
                <div className="mb-4">
                  <div className="text-5xl mb-2 filter drop-shadow-lg">{prayer.icon}</div>
                  <h4 className="text-xl font-bold text-gray-800 mb-1">{prayer.name}</h4>
                </div>
                
                <div className={`
                  bg-white rounded-xl p-4 shadow-inner border-2 ${prayer.borderColor}
                  ${prayer.isCurrent ? 'bg-green-50 border-green-400' : ''}
                `}>
                  <div className="text-3xl font-bold text-gray-900 mb-1 arabic-time">
                    {prayer.time}
                  </div>
                  
                  {prayer.isCurrent && (
                    <div className="text-sm text-green-600 font-semibold mt-2">
                      {language === 'kurdish' ? 'کاتی ئێستا' : 'الوقت الحالي'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Next Prayer Info */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-gray-200">
          <div className="text-center">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">
              {language === 'kurdish' ? 'نوێژی داهاتوو' : 'الصلاة القادمة'}
            </h4>
            <div className="flex items-center justify-center space-x-4">
              <div className="text-2xl">⏰</div>
              <div>
                <p className="text-lg font-bold text-green-700">
                  {prayers.find(p => p.isCurrent)?.name || prayers[0].name}
                </p>
                <p className="text-sm text-gray-600">
                  {language === 'kurdish' ? 'کات لەگەڵ ئێوەدایە' : 'حان وقت الصلاة'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderQibla = () => {
    if (!selectedCity) {
      return (
        <div className="text-center py-8 text-gray-600">
          {currentLang.selectCity}
        </div>
      );
    }

    if (loading) {
      return (
        <div className="text-center py-8">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">{currentLang.loading}</p>
        </div>
      );
    }

    if (!qiblaDirection) {
      return (
        <div className="text-center py-8 text-gray-600">
          {currentLang.loading}
        </div>
      );
    }

    return (
      <div className="text-center space-y-6">
        <div>
          <h3 className="text-xl font-bold text-green-800 mb-2">{currentLang.qiblaDirection}</h3>
          <p className="text-gray-600">{selectedCity.name}</p>
        </div>
        
        <div className="qibla-compass bg-white rounded-full w-64 h-64 mx-auto relative shadow-lg border-8 border-green-200">
          <div className="absolute inset-4 rounded-full border-2 border-green-300">
            <div 
              className="absolute top-0 left-1/2 w-1 h-8 bg-red-600 transform -translate-x-1/2 rounded-full"
              style={{ 
                transformOrigin: 'bottom center',
                transform: `translateX(-50%) rotate(${qiblaDirection.qibla_direction}deg)`
              }}
            ></div>
            <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-green-600 rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-sm font-bold text-gray-700">N</div>
            <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-sm font-bold text-gray-700">S</div>
            <div className="absolute left-2 top-1/2 transform -translate-y-1/2 text-sm font-bold text-gray-700">W</div>
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 text-sm font-bold text-gray-700">E</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-lg font-semibold text-green-800">
            {qiblaDirection.qibla_direction}°
          </p>
          <p className="text-sm text-gray-600 mt-2">
            🕋 {language === 'kurdish' ? 'ئاراستەی مەکە' : 'اتجاه مكة المكرمة'}
          </p>
        </div>
      </div>
    );
  };

  const renderDuas = () => {
    if (!duas) {
      return (
        <div className="text-center py-8 text-gray-600">
          {currentLang.loading}
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-bold text-green-800 mb-4">{currentLang.morningDuas}</h3>
          <div className="space-y-4">
            {duas.morning_duas?.map((dua) => (
              <div key={dua.id} className="dua-card bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
                <h4 className="font-bold text-green-700 mb-3">
                  {language === 'kurdish' ? dua.title_kurdish : dua.title_arabic}
                </h4>
                <div className="space-y-3">
                  <p className="text-xl text-right arabic-text" dir="rtl">{dua.arabic}</p>
                  <p className="text-lg text-right kurdish-text" dir="rtl">
                    {language === 'kurdish' ? dua.kurdish : dua.arabic}
                  </p>
                  <p className="text-sm text-gray-600 italic">{dua.transliteration}</p>
                  <p className="text-sm text-gray-700">
                    {language === 'kurdish' ? dua.translation_kurdish : dua.translation_english}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-bold text-green-800 mb-4">{currentLang.eveningDuas}</h3>
          <div className="space-y-4">
            {duas.evening_duas?.map((dua) => (
              <div key={dua.id} className="dua-card bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
                <h4 className="font-bold text-blue-700 mb-3">
                  {language === 'kurdish' ? dua.title_kurdish : dua.title_arabic}
                </h4>
                <div className="space-y-3">
                  <p className="text-xl text-right arabic-text" dir="rtl">{dua.arabic}</p>
                  <p className="text-lg text-right kurdish-text" dir="rtl">
                    {language === 'kurdish' ? dua.kurdish : dua.arabic}
                  </p>
                  <p className="text-sm text-gray-600 italic">{dua.transliteration}</p>
                  <p className="text-sm text-gray-700">
                    {language === 'kurdish' ? dua.translation_kurdish : dua.translation_english}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderQuran = () => {
    if (!quranSurahs.length) {
      return (
        <div className="text-center py-8 text-gray-600">
          {currentLang.loading}
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Surah Selector */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-amber-200">
          <div className="text-center mb-4">
            <h3 className="text-xl font-bold text-amber-800 mb-2">{currentLang.quran}</h3>
          </div>
          
          <div className="max-w-md mx-auto">
            <select
              onChange={handleSurahChange}
              className="w-full bg-white text-amber-700 px-4 py-3 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-amber-300 border-2 border-amber-300"
            >
              <option value="">{currentLang.selectSurah}</option>
              {quranSurahs.map((surah) => (
                <option key={surah.number} value={surah.number}>
                  {surah.number}. {language === 'kurdish' ? surah.name_kurdish : surah.name_arabic}
                  {' '}({surah.verses_count} {currentLang.verses})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Surah Display */}
        {selectedSurah && (
          <div className="space-y-6">
            {/* Surah Info Header */}
            <div className="bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-2xl p-6 shadow-lg">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">
                  {language === 'kurdish' 
                    ? selectedSurah.surah_info.name_kurdish 
                    : selectedSurah.surah_info.name_arabic}
                </h2>
                <p className="text-amber-100 text-lg mb-2">
                  {selectedSurah.surah_info.name_english}
                </p>
                <div className="flex justify-center items-center space-x-4 text-sm">
                  <span className="bg-amber-600 px-3 py-1 rounded-full">
                    {language === 'kurdish' ? 'ژمارە' : 'رقم'}: {selectedSurah.surah_info.number}
                  </span>
                  <span className="bg-amber-600 px-3 py-1 rounded-full">
                    {selectedSurah.total_verses} {currentLang.verses}
                  </span>
                  <span className="bg-amber-600 px-3 py-1 rounded-full">
                    {selectedSurah.surah_info.type}
                  </span>
                </div>
              </div>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="text-center py-8">
                <div className="spinner mx-auto mb-4"></div>
                <p className="text-gray-600">{currentLang.loading}</p>
              </div>
            )}

            {/* Verses Display */}
            {!loading && selectedSurah.verses && (
              <div className="space-y-4">
                {selectedSurah.verses.map((verse) => (
                  <div key={verse.verse_number} className="quran-card bg-white rounded-lg shadow-md p-6 border-t-4 border-amber-500">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm bg-amber-100 text-amber-800 px-3 py-1 rounded-full font-bold">
                        {language === 'kurdish' ? `ئایەت ${verse.verse_number}` : `آية ${verse.verse_number}`}
                      </span>
                    </div>
                    
                    <div className="space-y-4">
                      <p className="text-2xl text-right arabic-text leading-relaxed" dir="rtl">
                        {verse.arabic}
                      </p>
                      
                      <p className="text-lg text-right kurdish-text" dir="rtl">
                        {language === 'kurdish' ? verse.kurdish : verse.arabic}
                      </p>
                      
                      <p className="text-sm text-gray-600 italic">
                        {verse.transliteration}
                      </p>
                      
                      <p className="text-sm text-gray-700 border-t pt-3">
                        {verse.english}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderSettings = () => {
    if (!settings) {
      return (
        <div className="text-center py-8 text-gray-600">
          {currentLang.loading}
        </div>
      );
    }

    const handleSettingChange = (key, value) => {
      const newSettings = { ...settings, [key]: value };
      setSettings(newSettings);
    };

    const handleSaveSettings = () => {
      updateSettings(settings);
    };

    return (
      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-blue-200">
          <h3 className="text-xl font-bold text-blue-800 mb-4 flex items-center">
            ⚙️ {currentLang.generalSettings}
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.theme}</label>
              <select
                value={settings.theme}
                onChange={(e) => handleSettingChange('theme', e.target.value)}
                className="bg-white border-2 border-blue-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option value="default">{language === 'kurdish' ? 'بنەڕەتی' : 'افتراضي'}</option>
                <option value="dark">{language === 'kurdish' ? 'تاریک' : 'داكن'}</option>
                <option value="light">{language === 'kurdish' ? 'ڕووناک' : 'فاتح'}</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.fontSize}</label>
              <select
                value={settings.font_size}
                onChange={(e) => handleSettingChange('font_size', e.target.value)}
                className="bg-white border-2 border-blue-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option value="small">{language === 'kurdish' ? 'بچووک' : 'صغير'}</option>
                <option value="medium">{language === 'kurdish' ? 'ناوەند' : 'متوسط'}</option>
                <option value="large">{language === 'kurdish' ? 'گەورە' : 'كبير'}</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.arabicFont}</label>
              <select
                value={settings.arabic_font}
                onChange={(e) => handleSettingChange('arabic_font', e.target.value)}
                className="bg-white border-2 border-blue-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option value="amiri">Amiri</option>
                <option value="scheherazade">Scheherazade</option>
                <option value="noto">Noto Sans Arabic</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-green-200">
          <h3 className="text-xl font-bold text-green-800 mb-4 flex items-center">
            🔔 {currentLang.notificationSettings}
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.prayerNotifications}</label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.prayer_notifications}
                  onChange={(e) => handleSettingChange('prayer_notifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.prayerSound}</label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.prayer_sound}
                  onChange={(e) => handleSettingChange('prayer_sound', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">{currentLang.hijriCalendar}</label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.hijri_calendar}
                  onChange={(e) => handleSettingChange('hijri_calendar', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="text-center">
          <button
            onClick={handleSaveSettings}
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-3 rounded-lg font-bold shadow-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 transform hover:scale-105"
          >
            💾 {currentLang.save}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50" dir={language === 'arabic' ? 'rtl' : 'ltr'}>
      {/* Header */}
      <header className="bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <h1 className="text-2xl md:text-3xl font-bold text-center md:text-left">
              🕌 {currentLang.title}
            </h1>
            
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 items-center">
              {/* Language Selector */}
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-white text-green-700 px-4 py-2 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-green-300"
              >
                <option value="kurdish">کوردی</option>
                <option value="arabic">العربية</option>
              </select>
              
              {/* City Selector */}
              <select
                value={selectedCity?.id || ''}
                onChange={handleCityChange}
                className="bg-white text-green-700 px-4 py-2 rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-green-300"
              >
                <option value="">{currentLang.selectCity}</option>
                {cities.map((city) => (
                  <option key={city.id} value={city.id}>
                    {city.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow-md sticky top-0 z-10">
        <div className="container mx-auto px-4">
          <div className="flex overflow-x-auto">
            {[
              { id: 'prayer-times', label: currentLang.prayerTimes, icon: '🕐' },
              { id: 'qibla', label: currentLang.qibla, icon: '🧭' },
              { id: 'duas', label: currentLang.duas, icon: '🤲' },
              { id: 'quran', label: currentLang.quran, icon: '📖' },
              { id: 'settings', label: currentLang.settings, icon: '⚙️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 font-semibold transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'text-green-600 border-b-2 border-green-600 bg-green-50'
                    : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'prayer-times' && renderPrayerTimes()}
        {activeTab === 'qibla' && renderQibla()}
        {activeTab === 'duas' && renderDuas()}
        {activeTab === 'quran' && renderQuran()}
        {activeTab === 'settings' && renderSettings()}
      </main>

      {/* Footer */}
      <footer className="bg-green-800 text-white text-center py-6 mt-12">
        <p className="mb-2">🕌 {currentLang.title}</p>
        <p className="text-green-200 text-sm">
          {language === 'kurdish' 
            ? 'بۆ خزمەتکردنی کۆمەڵگای موسڵمان' 
            : 'خدمة للمجتمع المسلم'}
        </p>
      </footer>
    </div>
  );
};

export default App;