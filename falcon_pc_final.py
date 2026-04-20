#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FALCON TEAM PC v2.0 (ПОЛНЫЙ ФАРШ)

import os
import sys
import json
import sqlite3
from datetime import datetime
import urllib.parse
import time
import random
import threading
import traceback

# Устанавливаем кодировку для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Цвета
class C:
    RED = '\033[91m'
    GRN = '\033[92m'
    YEL = '\033[93m'
    BLU = '\033[94m'
    CYN = '\033[96m'
    WHT = '\033[97m'
    BLD = '\033[1m'
    RST = '\033[0m'
    GRY = '\033[90m'

# ========== ПРОВЕРКА БИБЛИОТЕК ==========
try:
    import requests
except ImportError:
    print(f"{C.RED}[!] Ошибка: библиотека 'requests' не установлена.{C.RST}")
    print(f"{C.YEL}Установи: pip install requests{C.RST}")
    sys.exit(1)

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    print(f"{C.YEL}[!] whois не установлен. Установка: pip install python-whois{C.RST}")

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    print(f"{C.YEL}[!] phonenumbers не установлен. Установка: pip install phonenumbers{C.RST}")

# ========== БАЗА ДАННЫХ ==========
DB_PATH = "falcon_pc.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY, 
                  title TEXT, 
                  data TEXT, 
                  timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cache
                 (key TEXT PRIMARY KEY,
                  value TEXT,
                  expires TEXT)''')
    conn.commit()
    conn.close()

def save_to_cache(key, value, ttl_hours=24):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        expires = (datetime.now().timestamp() + ttl_hours * 3600)
        c.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)", (key, value, str(expires)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Кеш ошибка: {e}")

def get_from_cache(key):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value, expires FROM cache WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        if row and float(row[1]) > datetime.now().timestamp():
            return row[0]
    except:
        pass
    return None

def save_report(title, data):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO reports (title, data, timestamp) VALUES (?, ?, ?)",
                  (title, json.dumps(data, ensure_ascii=False), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"{C.GRN}✅ Отчёт сохранён: {title}{C.RST}")
    except Exception as e:
        print(f"{C.RED}Ошибка сохранения отчёта: {e}{C.RST}")

# ========== МОЩНЫЙ ПОИСК ПО НОМЕРУ (ПОЛНЫЙ ФАРШ) ==========
def scan_phone_powerful(phone):
    """Мощный поиск по номеру: 60-90 секунд, 40+ источников"""
    
    print(f"\n{C.BLD}{C.CYN}{'='*70}{C.RST}")
    print(f"{C.BLD}{C.CYN}🔍 МОЩНЫЙ ПОИСК ПО НОМЕРУ: {phone}{C.RST}")
    print(f"{C.BLD}{C.CYN}{'='*70}{C.RST}")
    print(f"{C.YEL}⏳ Поиск займёт 60-90 секунд...{C.RST}")
    
    # Очистка номера
    clean = ''.join(c for c in phone if c.isdigit())
    if clean.startswith('8'):
        clean = '7' + clean[1:]
    elif not clean.startswith('7') and len(clean) == 10:
        clean = '7' + clean
    
    results = {
        "phone": f"+{clean}",
        "sources": [],
        "links": [],
        "api_results": {}
    }
    
    start_time = time.time()
    
    # ========== 1. БАЗОВАЯ ИНФОРМАЦИЯ (phonenumbers) ==========
    print(f"\n{C.BLD}{C.CYN}[1/9] БАЗОВАЯ ИНФОРМАЦИЯ...{C.RST}")
    if PHONENUMBERS_AVAILABLE:
        try:
            parsed = phonenumbers.parse(f"+{clean}", None)
            country = geocoder.country_name_for_number(parsed, "ru")
            operator = carrier.name_for_number(parsed, "ru")
            region = geocoder.description_for_number(parsed, "ru")
            
            print(f"  {C.GRN}✅ Страна:{C.RST} {country or 'Не определена'}")
            print(f"  {C.GRN}✅ Оператор:{C.RST} {operator or 'Не определён'}")
            print(f"  {C.GRN}✅ Регион:{C.RST} {region or 'Не определён'}")
            
            # Тип номера
            if len(clean) == 11:
                city_codes = ['495', '499', '812', '831', '846', '863', '343', '381', '383', '391']
                if clean[1:4] in city_codes:
                    phone_type = "Городской (стационарный)"
                else:
                    phone_type = "Мобильный"
            else:
                phone_type = "Не определён"
            print(f"  {C.GRN}✅ Тип номера:{C.RST} {phone_type}")
            
            try:
                tz = timezone.time_zones_for_number(parsed)
                print(f"  {C.GRN}✅ Часовой пояс:{C.RST} {', '.join(tz) if tz else 'Не определён'}")
            except:
                pass
                
            results["sources"].append({"source": "phonenumbers", "data": {"country": country, "operator": operator, "region": region}})
        except Exception as e:
            print(f"  {C.YEL}⚠️ Ошибка: {e}{C.RST}")
    else:
        # fallback база кодов
        codes = {
            "910": "МТС", "911": "МТС", "912": "МТС", "913": "МТС", "914": "МТС",
            "915": "МТС", "916": "МТС", "917": "МТС", "918": "МТС", "919": "МТС",
            "920": "Мегафон", "921": "Мегафон", "922": "Мегафон", "923": "Мегафон", "924": "Мегафон",
            "925": "Мегафон", "926": "Мегафон", "927": "Мегафон", "928": "Мегафон", "929": "Мегафон",
            "960": "Билайн", "961": "Билайн", "962": "Билайн", "963": "Билайн", "964": "Билайн",
            "965": "Билайн", "966": "Билайн", "967": "Билайн", "968": "Билайн", "969": "Билайн",
            "900": "Tele2", "901": "Tele2", "902": "Tele2", "903": "Tele2", "904": "Tele2",
            "905": "Tele2", "906": "Tele2", "908": "Tele2", "950": "Tele2", "951": "Tele2"
        }
        code = clean[:3]
        if code in codes:
            print(f"  {C.GRN}✅ Оператор:{C.RST} {codes[code]}")
        else:
            print(f"  {C.YEL}⚠️ Оператор не определён{C.RST}")
    
    time.sleep(1)
    
    # ========== 2. EPIEOS API ==========
    print(f"\n{C.BLD}{C.CYN}[2/9] EPIEOS (сервисы и соцсети)...{C.RST}")
    try:
        url = f"https://epieos.com/api/phone/{clean}"
        r = requests.get(url, timeout=10, headers={"User-Agent": "FalconTeam/1.0"})
        if r.status_code == 200:
            data = r.json()
            services = data.get("services", {})
            found_services = []
            for service, info in services.items():
                if isinstance(info, dict) and info.get("exists", False):
                    found_services.append(service)
                elif isinstance(info, bool) and info:
                    found_services.append(service)
            if found_services:
                print(f"  {C.GRN}✅ Найден в сервисах:{C.RST} {', '.join(found_services[:10])}")
                results["api_results"]["epieos"] = found_services
            else:
                print(f"  {C.YEL}⚠️ Не найден в публичных сервисах{C.RST}")
        else:
            print(f"  {C.YEL}⚠️ EPIEOS не отвечает (код {r.status_code}){C.RST}")
    except Exception as e:
        print(f"  {C.YEL}⚠️ Ошибка EPIEOS: {e}{C.RST}")
    
    time.sleep(2)
    
    # ========== 3. TRUECALLER ==========
    print(f"\n{C.BLD}{C.CYN}[3/9] TRUECALLER (метки и отзывы)...{C.RST}")
    truecaller_url = f"https://www.truecaller.com/search/{clean}"
    print(f"  {C.CYN}Truecaller:{C.RST} {truecaller_url}")
    results["links"].append({"site": "Truecaller", "url": truecaller_url})
    
    # ========== 4. GETCONTACT ==========
    print(f"\n{C.BLD}{C.CYN}[4/9] GETCONTACT (метки в телефонных книгах)...{C.RST}")
    getcontact_url = f"https://getcontact.com/ru/search/{clean}"
    print(f"  {C.CYN}GetContact:{C.RST} {getcontact_url}")
    results["links"].append({"site": "GetContact", "url": getcontact_url})
    
    time.sleep(1)
    
    # ========== 5. СОЦИАЛЬНЫЕ СЕТИ ==========
    print(f"\n{C.BLD}{C.CYN}[5/9] СОЦИАЛЬНЫЕ СЕТИ...{C.RST}")
    
    social_links = [
        ("Telegram", f"https://t.me/+{clean}"),
        ("WhatsApp", f"https://wa.me/{clean}"),
        ("Viber", f"viber://add?number={clean}"),
        ("VK", f"https://vk.com/people/{clean}"),
        ("OK", f"https://ok.ru/search?st.query={clean}"),
        ("Instagram", f"https://www.instagram.com/accounts/account_recovery/?phone={clean}"),
        ("Facebook", f"https://www.facebook.com/search/top/?q={clean}"),
        ("Twitter", f"https://twitter.com/search?q={clean}")
    ]
    
    for name, url in social_links:
        print(f"  {C.CYN}{name}:{C.RST} {url}")
        results["links"].append({"site": name, "url": url})
        time.sleep(0.3)
    
    # ========== 6. БАЗЫ МОШЕННИКОВ ==========
    print(f"\n{C.BLD}{C.CYN}[6/9] БАЗЫ МОШЕННИКОВ И ОТЗЫВЫ...{C.RST}")
    
    fraud_links = [
        ("Nomer.io", f"https://nomer.io/info/{clean}"),
        ("Tellows", f"https://www.tellows.ru/num/{clean}"),
        ("OKI", f"https://okis.ru/?search={clean}"),
        ("KtoZvonit", f"https://ktozvonit.ru/nomer/{clean}"),
        ("Zvonili", f"https://zvonili.com/number/{clean}"),
        ("PhoneRadar", f"https://phoneradar.ru/nomer/{clean}")
    ]
    
    for name, url in fraud_links:
        print(f"  {C.CYN}{name}:{C.RST} {url}")
        results["links"].append({"site": name, "url": url})
        time.sleep(0.3)
    
    # ========== 7. ОБЪЯВЛЕНИЯ И КОНТАКТЫ ==========
    print(f"\n{C.BLD}{C.CYN}[7/9] ОБЪЯВЛЕНИЯ И КОНТАКТЫ...{C.RST}")
    
    ad_links = [
        ("Avito", f"https://www.avito.ru/all?q={clean}"),
        ("Юла", f"https://youla.ru/search?q={clean}"),
        ("2GIS", f"https://2gis.ru/search/{clean}"),
        ("OLX", f"https://www.olx.ua/list/q-{clean}/")
    ]
    
    for name, url in ad_links:
        print(f"  {C.CYN}{name}:{C.RST} {url}")
        results["links"].append({"site": name, "url": url})
        time.sleep(0.3)
    
    # ========== 8. ПОИСКОВЫЕ СИСТЕМЫ ==========
    print(f"\n{C.BLD}{C.CYN}[8/9] ПОИСКОВЫЕ СИСТЕМЫ И SEO...{C.RST}")
    
    search_links = [
        ("Google", f"https://www.google.com/search?q=%22{clean}%22"),
        ("Yandex", f"https://yandex.ru/search/?text=%22{clean}%22"),
        ("Bing", f"https://www.bing.com/search?q=%22{clean}%22"),
        ("Whois", f"https://whois.domaintools.com/?query={clean}"),
        ("Spytox", f"https://spytox.com/search/{clean}")
    ]
    
    for name, url in search_links:
        print(f"  {C.CYN}{name}:{C.RST} {url}")
        results["links"].append({"site": name, "url": url})
        time.sleep(0.3)
    
    # ========== 9. ДОПОЛНИТЕЛЬНЫЕ БАЗЫ ==========
    print(f"\n{C.BLD}{C.CYN}[9/9] ДОПОЛНИТЕЛЬНЫЕ БАЗЫ И ИНСТРУМЕНТЫ...{C.RST}")
    
    extra_links = [
        ("Sync.me", f"https://sync.me/search/{clean}"),
        ("LeakCheck", "https://leakcheck.net/"),
        ("Search4Faces", "https://search4faces.com/"),
        ("VKWatch", "https://vk.watch/"),
        ("FindClone", "https://findclone.ru/"),
        ("Mobile-Locator", f"https://mobile-locator.com/?number={clean}"),
        ("EPIEOS", f"https://epieos.com/phone/{clean}")
    ]
    
    for name, url in extra_links:
        print(f"  {C.CYN}{name}:{C.RST} {url}")
        results["links"].append({"site": name, "url": url})
        time.sleep(0.3)
    
    # ========== TELEGRAM-БОТЫ ==========
    print(f"\n{C.BLD}{C.CYN}🤖 TELEGRAM-БОТЫ (ДЛЯ РУЧНОГО ПОИСКА):{C.RST}")
    
    bots = [
        ("Sherlock", "@sherlock_bot", "тысячи баз"),
        ("Vektor", "@vektor_bot", "поиск по телефону"),
        ("Enigma", "@enigma_bot", "универсальный поиск"),
        ("Himera", "@himera_bot", "легальный поиск"),
        ("Funstat", "@funstat_bot", "поиск по Telegram (/text)"),
        ("LeakOSINT", "@leakosint_bot", "поиск по миру")
    ]
    
    for name, username, desc in bots:
        print(f"  {C.CYN}{name}:{C.RST} {username} — {desc}")
    
    # ========== ИТОГИ ==========
    elapsed = time.time() - start_time
    results["elapsed"] = round(elapsed, 1)
    
    print(f"\n{C.BLD}{C.CYN}{'='*70}{C.RST}")
    print(f"{C.BLD}{C.GRN}📊 РЕЗУЛЬТАТЫ ПОИСКА:{C.RST}")
    print(f"  ⏱️  Время поиска: {elapsed:.1f} секунд")
    print(f"  🔗 Найдено ссылок: {len(results['links'])}")
    print(f"  🤖 Telegram-ботов: {len(bots)}")
    if results["api_results"].get("epieos"):
        print(f"  ✅ Найден в сервисах: {', '.join(results['api_results']['epieos'][:5])}")
    
    print(f"\n{C.BLD}{C.CYN}{'='*70}{C.RST}")
    print(f"{C.BLD}{C.GRN}📢 ВЗЯТО С ОТКРЫТЫХ ИСТОЧНИКОВ.{C.RST}")
    print(f"{C.BLD}{C.GRN}   НИЧЕГО НЕ НАРУШАЕТ ЗАКОН.{C.RST}")
    print(f"{C.BLD}{C.GRN}   ПОИСК ПО НОМЕРУ ПО ОТКРЫТЫМ БД.{C.RST}")
    print(f"{C.CYN}🤖 Для углублённого поиска используйте Telegram-ботов выше.{C.RST}")
    print(f"{C.BLD}{C.CYN}{'='*70}{C.RST}")
    
    return results

# ========== ФУНКЦИИ ПОИСКА ==========
def scan_email(email):
    print(f"\n{C.BLD}{C.CYN}[*] Сканирование email: {email}{C.RST}")
    result = {"email": email, "hibp": False, "breaches": [], "valid": True}
    
    if "@" not in email or "." not in email.split("@")[1]:
        result["valid"] = False
        print(f"{C.RED}❌ Неверный формат email{C.RST}")
        return result
    
    cache_key = f"hibp_{email}"
    cached = get_from_cache(cache_key)
    if cached:
        result["hibp"] = cached == "found"
        print(f"{C.GRN}✅ (кеш) Утечек: {result['hibp']}{C.RST}")
    else:
        try:
            headers = {"User-Agent": "FalconTeam/1.0"}
            r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers=headers, timeout=10)
            if r.status_code == 200:
                breaches = [b["Name"] for b in r.json()]
                result["hibp"] = True
                result["breaches"] = breaches
                save_to_cache(cache_key, "found")
                print(f"{C.RED}⚠️ Найден в утечках: {', '.join(breaches[:3])}{C.RST}")
            elif r.status_code == 404:
                save_to_cache(cache_key, "not_found")
                print(f"{C.GRN}✅ Не найден в утечках{C.RST}")
            else:
                print(f"{C.YEL}❓ HIBP ошибка: {r.status_code}{C.RST}")
        except Exception as e:
            print(f"{C.YEL}❓ HIBP недоступен: {e}{C.RST}")
    
    return result

def scan_ip(ip):
    print(f"\n{C.BLD}{C.CYN}[*] Сканирование IP: {ip}{C.RST}")
    result = {"ip": ip, "country": None, "city": None, "isp": None}
    
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = r.json()
        if data["status"] == "success":
            result["country"] = data.get("country")
            result["city"] = data.get("city")
            result["isp"] = data.get("isp")
            print(f"{C.GRN}✅ Страна: {result['country']}{C.RST}")
            print(f"{C.GRN}✅ Город: {result['city']}{C.RST}")
            print(f"{C.GRN}✅ ISP: {result['isp']}{C.RST}")
        else:
            print(f"{C.YEL}❓ IP не найден{C.RST}")
    except Exception as e:
        print(f"{C.YEL}❓ Ошибка геолокации: {e}{C.RST}")
    
    return result

def scan_username(username):
    print(f"\n{C.BLD}{C.CYN}[*] Поиск username: {username}{C.RST}")
    sites = {
        "VK": f"https://vk.com/{username}",
        "Telegram": f"https://t.me/{username}",
        "GitHub": f"https://github.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "OK": f"https://ok.ru/{username}"
    }
    
    found = []
    for name, url in sites.items():
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                found.append({"site": name, "url": url})
                print(f"{C.GRN}✅ {name}: {url}{C.RST}")
            else:
                print(f"{C.RED}❌ {name}: не найден{C.RST}")
        except:
            print(f"{C.YEL}❓ {name}: ошибка{C.RST}")
        time.sleep(0.2)
    
    return found

def scan_domain(domain):
    print(f"\n{C.BLD}{C.CYN}[*] WHOIS: {domain}{C.RST}")
    result = {"domain": domain, "registrar": None, "creation": None}
    
    if not WHOIS_AVAILABLE:
        print(f"{C.YEL}❌ whois не установлен{C.RST}")
        return result
    
    try:
        w = whois.whois(domain)
        result["registrar"] = str(w.registrar) if w.registrar else None
        result["creation"] = str(w.creation_date) if w.creation_date else None
        print(f"{C.GRN}✅ Регистратор: {result['registrar']}{C.RST}")
        print(f"{C.GRN}✅ Создан: {result['creation']}{C.RST}")
    except Exception as e:
        print(f"{C.YEL}❓ Не удалось получить WHOIS: {e}{C.RST}")
    
    return result

# ========== ОСНОВНАЯ ЛОГИКА ==========
def show_help():
    print(f"""
{C.BLD}{C.CYN}ДОСТУПНЫЕ КОМАНДЫ:{C.RST}
  {C.WHT}email <адрес>{C.RST}      - проверить email
  {C.WHT}phone <номер>{C.RST}      - МОЩНЫЙ поиск по номеру (40+ источников)
  {C.WHT}ip <адрес>{C.RST}         - проверить IP
  {C.WHT}user <ник>{C.RST}         - поиск по username
  {C.WHT}domain <домен>{C.RST}     - WHOIS домена
  {C.WHT}report <тип> <значение>{C.RST} - сгенерировать отчёт
  {C.WHT}help{C.RST}               - эта справка
  {C.WHT}clear{C.RST}              - очистить экран
  {C.WHT}exit{C.RST}               - выход
""")

def main():
    try:
        init_db()
    except Exception as e:
        print(f"{C.RED}Ошибка инициализации БД: {e}{C.RST}")
    
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{C.BLD}{C.RED}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     ███████╗ █████╗ ██╗      ██████╗ ███╗   ██╗      ║")
    print("║     ██╔════╝██╔══██╗██║     ██╔═══██╗████╗  ██║      ║")
    print("║     █████╗  ██║  ██║██║     ██║   ██║██╔██╗ ██║      ║")
    print("║     ██╔══╝  ██║  ██║██║     ██║   ██║██║╚██╗██║      ║")
    print("║     ██║     ╚█████╔╝███████╗╚██████╔╝██║ ╚████║      ║")
    print("║     ╚═╝      ╚════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝      ║")
    print("║                  FALCON TEAM PC v2.0                  ║")
    print("║                     ПОЛНЫЙ ФАРШ                       ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"{C.RST}")
    print(f"{C.GRY}OSINT-терминал для проверки данных. Введите 'help' для списка команд.{C.RST}\n")
    
    while True:
        try:
            cmd = input(f"{C.BLD}{C.RED}FALCON>{C.RST} ").strip().lower()
            if not cmd:
                continue
            
            parts = cmd.split()
            action = parts[0]
            
            if action == "exit":
                print(f"{C.RED}Выход...{C.RST}")
                break
            
            elif action == "help":
                show_help()
            
            elif action == "clear":
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            elif action == "email" and len(parts) > 1:
                result = scan_email(parts[1])
                if result:
                    print(f"\n{C.GRN}📊 Результат:{C.RST}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            
            elif action == "phone" and len(parts) > 1:
                result = scan_phone_powerful(parts[1])
                if result:
                    print(f"\n{C.GRN}📊 Результат:{C.RST}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            
            elif action == "ip" and len(parts) > 1:
                result = scan_ip(parts[1])
                if result:
                    print(f"\n{C.GRN}📊 Результат:{C.RST}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            
            elif action == "user" and len(parts) > 1:
                result = scan_username(parts[1])
                if result:
                    print(f"\n{C.GRN}📊 Найдено профилей: {len(result)}{C.RST}")
            
            elif action == "domain" and len(parts) > 1:
                result = scan_domain(parts[1])
                if result:
                    print(f"\n{C.GRN}📊 Результат:{C.RST}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
            
            elif action == "report" and len(parts) > 2:
                target_type = parts[1]
                target_value = parts[2]
                data = None
                
                if target_type == "email":
                    data = scan_email(target_value)
                elif target_type == "phone":
                    data = scan_phone_powerful(target_value)
                elif target_type == "ip":
                    data = scan_ip(target_value)
                elif target_type == "user":
                    data = scan_username(target_value)
                elif target_type == "domain":
                    data = scan_domain(target_value)
                else:
                    print(f"{C.RED}❌ Неизвестный тип. Доступно: email, phone, ip, user, domain{C.RST}")
                    continue
                
                if data:
                    save_report(f"{target_type}_{target_value}", data)
            
            else:
                print(f"{C.RED}❌ Неизвестная команда. Введите 'help'.{C.RST}")
        
        except KeyboardInterrupt:
            print(f"\n{C.YEL}Прервано. Введите 'exit' для выхода.{C.RST}")
        except Exception as e:
            print(f"{C.RED}Ошибка: {e}{C.RST}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
