#!/usr/bin/env python3
"""
Kalasetu - Backend Bridge / Local API Service
Exposes local API endpoints, manages local caches, and orchestrates
calls to Kalachakra, Kalotsavachakra, and Kalakosha.
"""
import sys
import os
import json
import datetime
import uuid
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import Kalachakra
import Kalotsavachakra
import Kalakosha

CONFIG_DIR = os.path.expanduser("~/.config/kalayantra")
CUSTOM_CITIES_PATH = os.path.join(CONFIG_DIR, "custom_cities.json")
CUSTOM_OBSERVANCES_PATH = os.path.join(CONFIG_DIR, "custom_observances.json")
REMINDERS_PATH = os.path.join(CONFIG_DIR, "reminders.json")
NOTIFICATION_CACHE_PATH = os.path.join(CONFIG_DIR, "notification_cache.json")
LAST_COORDS_PATH = os.path.join(CONFIG_DIR, "last_coordinates.json")

reminder_wakeup_event = threading.Event()

# Simple memory cache for API requests
CACHE = {}

import logging

# Set up structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Kalasetu")

class ConfigManager:
    def __init__(self):
        self.lock = threading.RLock()
        self._custom_cities_cache = None
        self._custom_observances_cache = None
        self._all_observances_cache = None
        self._reminders_cache = None
        self._notification_cache = None
        self._last_coords_cache = None

    def ensure_config_exists(self):
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
            except Exception as e:
                logger.error(f"Failed to create config dir {CONFIG_DIR}: {e}")
        for path, default in [
            (CUSTOM_CITIES_PATH, []),
            (CUSTOM_OBSERVANCES_PATH, []),
            (REMINDERS_PATH, []),
            (NOTIFICATION_CACHE_PATH, {"date": "", "sent": []}),
            (LAST_COORDS_PATH, {"lat": 23.1765, "lon": 75.7885, "alt": 0.0, "tz": 5.5, "calendar_system": "shaka", "month_system": "amavasyanta", "lang": "en"})
        ]:
            if not os.path.exists(path):
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(default, f)
                except Exception as e:
                    logger.error(f"Failed to create default config at {path}: {e}")

    def load_custom_cities(self):
        if self._custom_cities_cache is not None:
            return json.loads(json.dumps(self._custom_cities_cache))
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(CUSTOM_CITIES_PATH, "r", encoding="utf-8") as f:
                    self._custom_cities_cache = json.load(f)
                    return json.loads(json.dumps(self._custom_cities_cache))
            except Exception as e:
                logger.error(f"Error loading custom cities: {e}")
                return []

    def save_custom_cities(self, cities):
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(CUSTOM_CITIES_PATH, "w", encoding="utf-8") as f:
                    json.dump(cities, f, indent=2, ensure_ascii=False)
                self._custom_cities_cache = cities
            except Exception as e:
                logger.error(f"Error saving custom cities: {e}")

    def load_custom_observances(self):
        if self._custom_observances_cache is not None:
            return json.loads(json.dumps(self._custom_observances_cache))
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(CUSTOM_OBSERVANCES_PATH, "r", encoding="utf-8") as f:
                    self._custom_observances_cache = json.load(f)
                    return json.loads(json.dumps(self._custom_observances_cache))
            except Exception as e:
                logger.error(f"Error loading custom observances: {e}")
                return []

    def save_custom_observances(self, observances):
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(CUSTOM_OBSERVANCES_PATH, "w", encoding="utf-8") as f:
                    json.dump(observances, f, indent=2, ensure_ascii=False)
                self._custom_observances_cache = observances
                self._all_observances_cache = None
            except Exception as e:
                logger.error(f"Error saving custom observances: {e}")

    def load_all_observances(self):
        if self._all_observances_cache is not None:
            return json.loads(json.dumps(self._all_observances_cache))
        
        public_obs = self.load_custom_observances()
        private_list = []
        private_dir = os.path.join(CONFIG_DIR, "private")
        
        for fn in ["private_observances.json", "private_tithis.json"]:
            p_path = os.path.join(private_dir, fn)
            if os.path.exists(p_path):
                try:
                    with open(p_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            private_list.extend(data)
                except Exception as e:
                    logger.warning(f"Failed to load private file {fn}: {e}")
                    
        if not private_list:
            self._all_observances_cache = public_obs
            return json.loads(json.dumps(self._all_observances_cache))
            
        with self.lock:
            public_keys = set()
            for o in public_obs:
                name = str(o.get("name") or o.get("title", "")).strip().lower()
                month = str(o.get("month") or o.get("masa", "")).strip()
                paksha = str(o.get("paksha", "")).strip()
                tithi = str(o.get("tithi", "")).strip()
                system = str(o.get("system", "amavasyanta")).strip().lower()
                public_keys.add((name, month, paksha, tithi, system))
                
            merged = list(public_obs)
            
            valid_months = {"Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"}
            valid_pakshas = {"Shukla", "Krishna"}
            valid_tithis = {"Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"}
            valid_systems = {"amavasyanta", "purnimanta"}
            
            for idx, item in enumerate(private_list):
                if not isinstance(item, dict):
                    logger.warning(f"Private tithi entry at index {idx} is not a dictionary; skipping.")
                    continue
                    
                name = str(item.get("title") or item.get("name", "")).strip()
                month = str(item.get("masa") or item.get("month", "")).strip()
                paksha = str(item.get("paksha", "")).strip()
                tithi = str(item.get("tithi", "")).strip()
                system = str(item.get("system", "amavasyanta")).strip().lower()
                
                if not name:
                    logger.warning(f"Private tithi entry at index {idx} has an empty name; skipping.")
                    continue
                if month not in valid_months:
                    logger.warning(f"Private tithi entry at index {idx} has invalid month/masa '{month}'; skipping.")
                    continue
                if paksha not in valid_pakshas:
                    logger.warning(f"Private tithi entry at index {idx} has invalid paksha '{paksha}'; skipping.")
                    continue
                if tithi not in valid_tithis:
                    logger.warning(f"Private tithi entry at index {idx} has invalid tithi '{tithi}'; skipping.")
                    continue
                if system not in valid_systems:
                    logger.warning(f"Private tithi entry at index {idx} has invalid system '{system}'; skipping.")
                    continue
                    
                greg_year = item.get("gregorian_year")
                if greg_year is not None and greg_year != "":
                    try:
                        greg_year = int(greg_year)
                    except ValueError:
                        logger.warning(f"Private tithi entry at index {idx} has invalid gregorian_year '{greg_year}'; skipping.")
                        continue
                else:
                    greg_year = None
                    
                item_id = item.get("id")
                if not item_id:
                    import uuid
                    item_id = "private_" + str(uuid.uuid4())[:8]
                    
                key = (name.lower(), month, paksha, tithi, system)
                if key in public_keys:
                    logger.warning(f"Private tithi entry '{name}' matches a public entry; skipping.")
                    continue
                    
                clean_item = {
                    "id": item_id,
                    "name": name,
                    "title": name,
                    "month": month,
                    "masa": month,
                    "paksha": paksha,
                    "tithi": tithi,
                    "system": system,
                    "gregorian_year": greg_year
                }
                merged.append(clean_item)
                
            self._all_observances_cache = merged
            return json.loads(json.dumps(self._all_observances_cache))

    def load_reminders(self):
        if self._reminders_cache is not None:
            return json.loads(json.dumps(self._reminders_cache))
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(REMINDERS_PATH, "r", encoding="utf-8") as f:
                    self._reminders_cache = json.load(f)
                    return json.loads(json.dumps(self._reminders_cache))
            except Exception as e:
                logger.error(f"Error loading reminders: {e}")
                return []

    def save_reminders(self, reminders):
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(REMINDERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(reminders, f, indent=2, ensure_ascii=False)
                self._reminders_cache = reminders
            except Exception as e:
                logger.error(f"Error saving reminders: {e}")

    def load_notification_cache(self):
        if self._notification_cache is not None:
            return json.loads(json.dumps(self._notification_cache))
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(NOTIFICATION_CACHE_PATH, "r", encoding="utf-8") as f:
                    self._notification_cache = json.load(f)
                    return json.loads(json.dumps(self._notification_cache))
            except Exception as e:
                logger.error(f"Error loading notification cache: {e}")
                return {"date": "", "sent": []}

    def save_notification_cache(self, cache):
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(NOTIFICATION_CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2, ensure_ascii=False)
                self._notification_cache = cache
            except Exception as e:
                logger.error(f"Error saving notification cache: {e}")

    def load_last_coordinates(self):
        if self._last_coords_cache is not None:
            return json.loads(json.dumps(self._last_coords_cache))
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(LAST_COORDS_PATH, "r", encoding="utf-8") as f:
                    self._last_coords_cache = json.load(f)
                    return json.loads(json.dumps(self._last_coords_cache))
            except Exception as e:
                logger.error(f"Error loading last coordinates: {e}")
                return {"lat": 23.1765, "lon": 75.7885, "alt": 0.0, "tz": 5.5, "calendar_system": "shaka", "month_system": "amavasyanta", "lang": "en"}

    def save_last_coordinates(self, coords):
        self.ensure_config_exists()
        with self.lock:
            try:
                with open(LAST_COORDS_PATH, "w", encoding="utf-8") as f:
                    json.dump(coords, f)
                self._last_coords_cache = coords
            except Exception as e:
                logger.error(f"Error saving last coordinates: {e}")

config_manager = ConfigManager()

def ensure_config_exists():
    config_manager.ensure_config_exists()

def load_custom_cities():
    return config_manager.load_custom_cities()

def save_custom_cities(cities):
    config_manager.save_custom_cities(cities)

def load_custom_observances():
    return config_manager.load_custom_observances()

def save_custom_observances(observances):
    config_manager.save_custom_observances(observances)

def load_all_observances():
    return config_manager.load_all_observances()

def load_reminders():
    return config_manager.load_reminders()

def save_reminders(reminders):
    config_manager.save_reminders(reminders)

def load_notification_cache():
    return config_manager.load_notification_cache()

def save_notification_cache(cache):
    config_manager.save_notification_cache(cache)

def load_last_coordinates():
    return config_manager.load_last_coordinates()

def save_last_coordinates(coords):
    config_manager.save_last_coordinates(coords)


def send_desktop_notification(title, body):
    try:
        import dbus
        session_bus = dbus.SessionBus()
        obj = session_bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
        interface = dbus.Interface(obj, 'org.freedesktop.Notifications')
        interface.Notify(
            'Kālayantra',
            dbus.UInt32(0),
            'office-calendar',
            str(title),
            str(body),
            dbus.Array([], signature='s'),
            dbus.Dictionary({}, signature='sv'),
            dbus.Int32(5000)
        )
    except Exception as e:
        print("Failed to send notification via dbus:", e)
        try:
            import subprocess
            subprocess.run(["notify-send", str(title), str(body), "--icon=office-calendar"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e2:
            print("Failed to send notification fallback:", e2)


def compute_trigger_time(reminder, astro_data):
    time_type = reminder.get("time_type", "sunrise")
    date_str = astro_data["date"]
    parts = date_str.split("-")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    
    def parse_hhmm(s):
        if not s or s == "--":
            return None
        try:
            hp, mp = s.split(":")
            return datetime.time(int(hp), int(mp))
        except Exception:
            return None

    if time_type == "sunrise":
        sunrise_time = parse_hhmm(astro_data.get("sunrise", "06:00"))
        if not sunrise_time:
            sunrise_time = datetime.time(6, 0)
        return datetime.datetime.combine(datetime.date(y, m, d), sunrise_time)
        
    elif time_type == "brahma_muhurta":
        bm_str = astro_data.get("brahma_muhurta", "04:30 - 05:15")
        try:
            start_str = bm_str.split("-")[0].strip()
            bm_time = parse_hhmm(start_str)
        except Exception:
            bm_time = None
        if not bm_time:
            bm_time = datetime.time(4, 30)
        return datetime.datetime.combine(datetime.date(y, m, d), bm_time)
        
    elif time_type == "offset_before_sunrise":
        sunrise_time = parse_hhmm(astro_data.get("sunrise", "06:00"))
        if not sunrise_time:
            sunrise_time = datetime.time(6, 0)
        sunrise_dt = datetime.datetime.combine(datetime.date(y, m, d), sunrise_time)
        offset = reminder.get("time_offset_mins", 0)
        try:
            offset = int(offset)
        except Exception:
            offset = 0
        return sunrise_dt - datetime.timedelta(minutes=offset)
        
    elif time_type == "exact_time":
        exact_time = parse_hhmm(reminder.get("time_exact_str", "09:00"))
        if not exact_time:
            exact_time = datetime.time(9, 0)
        return datetime.datetime.combine(datetime.date(y, m, d), exact_time)
        
    return datetime.datetime(y, m, d, 9, 0)


def reminder_daemon_loop():
    global reminder_wakeup_event
    while True:
        try:
            coords = load_last_coordinates()
            lat = coords["lat"]
            lon = coords["lon"]
            alt = coords["alt"]
            tz = coords["tz"]
            calendar_system = coords["calendar_system"]
            month_system = coords["month_system"]
            lang = coords["lang"]
            
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            now_local = (now_utc + datetime.timedelta(hours=tz)).replace(tzinfo=None)
            today = now_local.date()
            today_str = today.strftime("%Y-%m-%d")
            
            cache = load_notification_cache()
            if cache.get("date") != today_str:
                cache = {"date": today_str, "sent": []}
                save_notification_cache(cache)
                
            reminders = load_reminders()
            enabled_reminders = [r for r in reminders if r.get("enabled", True)]
            
            astro = Kalachakra.calculate_panchanga(
                today.year, today.month, today.day, tz, lat, lon, alt,
                calendar_system=calendar_system, month_system=month_system, lang=lang
            )
            
            custom_obs = load_all_observances()
            festivals = Kalotsavachakra.calculate_festivals(
                astro, tz, custom_obs, festival_rule="vaishnava", lang=lang
            )
            
            today_candidates = Kalotsavachakra.evaluate_reminders(astro, festivals, enabled_reminders, lang)
            
            pending_triggers = []
            sent_list = cache.get("sent", [])
            triggered_any = False
            
            for r in today_candidates:
                r_id = r.get("id")
                if r_id in sent_list:
                    continue
                    
                trigger_dt = compute_trigger_time(r, astro)
                if trigger_dt <= now_local:
                    send_desktop_notification(r.get("title", "Kālayantra Reminder"), r.get("description", ""))
                    sent_list.append(r_id)
                    cache["sent"] = sent_list
                    save_notification_cache(cache)
                    triggered_any = True
                else:
                    pending_triggers.append((trigger_dt, r))
                    
            if triggered_any:
                continue
                
            if pending_triggers:
                pending_triggers.sort(key=lambda x: x[0])
                next_dt, next_r = pending_triggers[0]
                sleep_secs = (next_dt - now_local).total_seconds()
                if sleep_secs < 1:
                    sleep_secs = 1
            else:
                tomorrow_start = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(0, 5))
                sleep_secs = (tomorrow_start - now_local).total_seconds()
                if sleep_secs < 10:
                    sleep_secs = 10
                    
            is_set = reminder_wakeup_event.wait(timeout=sleep_secs)
            if is_set:
                reminder_wakeup_event.clear()
                
        except Exception as e:
            print("Error in reminder daemon loop:", e)
            time.sleep(10)


class KalasetuRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        
        if url.path == '/day':
            self.handle_day(query)
        elif url.path == '/month':
            self.handle_month(query)
        elif url.path == '/search_city':
            self.handle_search_city(query)
        elif url.path == '/save_custom_city':
            self.handle_save_city(query)
        elif url.path == '/get_custom_observances':
            self.handle_get_observances()
        elif url.path == '/save_custom_observance':
            self.handle_save_observance(query)
        elif url.path == '/delete_custom_observance':
            self.handle_delete_observance(query)
        elif url.path == '/export_custom_observances':
            self.handle_export_observances(query)
        elif url.path == '/import_custom_observances':
            self.handle_import_observances(query)
        elif url.path == '/clear_custom_observances':
            self.handle_clear_observances()
        elif url.path == '/get_reminders':
            self.handle_get_reminders()
        elif url.path == '/save_reminder':
            self.handle_save_reminder(query)
        elif url.path == '/delete_reminder':
            self.handle_delete_reminder(query)
        elif url.path == '/clear_reminders':
            self.handle_clear_reminders()
        elif url.path == '/import_reminders':
            self.handle_import_reminders(query)
        elif url.path == '/export_reminders':
            self.handle_export_reminders(query)
        elif url.path == '/evaluate_reminders':
            self.handle_evaluate_reminders(query)
        elif url.path == '/system_info':
            self.handle_system_info()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_system_info(self):
        import platform
        info = {
            "architecture": platform.machine(),
            "system": platform.system(),
            "processor": platform.processor(),
        }
        self.send_json_response(200, info)

    def handle_day(self, query):
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            else:
                dt = datetime.datetime.now()
                date_str = dt.strftime("%Y-%m-%d")
                
            tithi_mode = query.get('tithi_mode', ['traditional'])[0]
            calendar_system = query.get('calendar_system', ['shaka'])[0]
            month_system = query.get('month_system', ['amavasyanta'])[0]
            festival_rule = query.get('festival_rule', ['vaishnava'])[0]
            lang = query.get('lang', ['en'])[0]

            # Save last used coordinates for background reminders thread
            coords = {
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "tz": tz,
                "calendar_system": calendar_system,
                "month_system": month_system,
                "lang": lang
            }
            save_last_coordinates(coords)

            # Cache key check (Only cache if it is NOT today!)
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            is_today = (date_str == today_str)

            clean_query = {k: v for k, v in query.items() if k not in ('_t', '_')}
            cache_key = ("day", json.dumps(clean_query, sort_keys=True))

            if not is_today and cache_key in CACHE:
                self.send_json_response(200, CACHE[cache_key])
                return

            # Compute astronomical data from Kalachakra
            astro_data = Kalachakra.calculate_panchanga(
                dt.year, dt.month, dt.day, tz, lat, lon, alt,
                tithi_mode, calendar_system, month_system, lang
            )
            
            # Load custom observances
            custom_obs = load_all_observances()
            
            # Compute festivals from Kalotsavachakra
            festivals = Kalotsavachakra.calculate_festivals(
                astro_data, tz, custom_obs, festival_rule, lang
            )
            
            # Merge festivals list into final JSON payload
            astro_data["festivals"] = festivals
            
            # Cache results if it is NOT today
            if not is_today:
                CACHE[cache_key] = astro_data

            self.send_json_response(200, astro_data)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_month(self, query):
        clean_query = {k: v for k, v in query.items() if k not in ('_t', '_')}
        cache_key = ("month", json.dumps(clean_query, sort_keys=True))
        if cache_key in CACHE:
            self.send_json_response(200, CACHE[cache_key])
            return
            
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            
            year = int(query.get('year', [datetime.datetime.now().year])[0])
            month = int(query.get('month', [datetime.datetime.now().month])[0])
            
            tithi_mode = query.get('tithi_mode', ['traditional'])[0]
            calendar_system = query.get('calendar_system', ['shaka'])[0]
            month_system = query.get('month_system', ['amavasyanta'])[0]
            festival_rule = query.get('festival_rule', ['vaishnava'])[0]
            lang = query.get('lang', ['en'])[0]
            
            if month == 12:
                next_month_start = datetime.date(year + 1, 1, 1)
            else:
                next_month_start = datetime.date(year, month + 1, 1)
            month_days = (next_month_start - datetime.date(year, month, 1)).days
            
            custom_obs = load_all_observances()
            
            days_data = []
            for d in range(1, month_days + 1):
                astro_data = Kalachakra.calculate_panchanga(
                    year, month, d, tz, lat, lon, alt,
                    tithi_mode, calendar_system, month_system, lang
                )
                festivals = Kalotsavachakra.calculate_festivals(
                    astro_data, tz, custom_obs, festival_rule, lang
                )
                astro_data["festivals"] = festivals
                days_data.append(astro_data)
                
            CACHE[cache_key] = days_data
            self.send_json_response(200, days_data)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_search_city(self, query):
        q = query.get('q', [''])[0].strip().lower()
        results = []
        
        # Load preset and custom cities
        presets = Kalakosha.BUILTIN_CITIES
        customs = load_custom_cities()
        combined = customs + presets # Custom cities take precedence
        
        seen = set()
        for city in combined:
            name = city["name"]
            if q in name.lower() and name.lower() not in seen:
                seen.add(name.lower())
                results.append(city)
                
        self.send_json_response(200, results[:15])

    def handle_save_city(self, query):
        try:
            name = query.get('name', [''])[0].strip()
            lat = float(query.get('lat', [0.0])[0])
            lon = float(query.get('lon', [0.0])[0])
            tz = float(query.get('tz', [0.0])[0])
            alt = float(query.get('alt', [0.0])[0])
            
            if not name:
                self.send_json_response(400, {"error": "Name cannot be empty"})
                return
                
            customs = load_custom_cities()
            # Check if exists, update or add
            exists = False
            for c in customs:
                if c["name"].lower() == name.lower():
                    c["lat"] = lat
                    c["lon"] = lon
                    c["tz"] = tz
                    c["alt"] = alt
                    exists = True
                    break
            if not exists:
                customs.append({
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "tz": tz,
                    "alt": alt
                })
            save_custom_cities(customs)
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_get_observances(self):
        obs = load_custom_observances()
        self.send_json_response(200, obs)

    def handle_save_observance(self, query):
        try:
            obs_id = query.get('id', [''])[0].strip()
            name = query.get('name', [''])[0].strip()
            month = query.get('month', [''])[0].strip()
            paksha = query.get('paksha', [''])[0].strip()
            tithi = query.get('tithi', [''])[0].strip()
            system = query.get('system', ['amavasyanta'])[0].strip()
            greg_year_str = query.get('gregorian_year', [''])[0].strip()
            gregorian_year = None
            if greg_year_str:
                try:
                    gregorian_year = int(greg_year_str)
                except ValueError:
                    self.send_json_response(400, {"error": "Gregorian year must be an integer"})
                    return
            
            if not name:
                self.send_json_response(400, {"error": "Name cannot be empty"})
                return
                
            obs = load_custom_observances()
            
            # Check for duplicate
            for o in obs:
                if (o["name"].lower() == name.lower() and 
                    o["month"] == month and 
                    o["paksha"] == paksha and 
                    o["tithi"] == tithi and 
                    o.get("system", "amavasyanta") == system):
                    if not obs_id or o["id"] != obs_id:
                        self.send_json_response(400, {"error": "Duplicate entry exists!"})
                        return
            if not obs_id:
                obs_id = str(uuid.uuid4())
                obs.append({
                    "id": obs_id,
                    "name": name,
                    "month": month,
                    "paksha": paksha,
                    "tithi": tithi,
                    "system": system,
                    "gregorian_year": gregorian_year
                })
            else:
                updated = False
                for o in obs:
                    if o["id"] == obs_id:
                        o["name"] = name
                        o["month"] = month
                        o["paksha"] = paksha
                        o["tithi"] = tithi
                        o["system"] = system
                        o["gregorian_year"] = gregorian_year
                        updated = True
                        break
                if not updated:
                    obs.append({
                        "id": obs_id,
                        "name": name,
                        "month": month,
                        "paksha": paksha,
                        "tithi": tithi,
                        "system": system,
                        "gregorian_year": gregorian_year
                    })
            save_custom_observances(obs)
            # Clear caches to reflect changes immediately
            CACHE.clear()
            self.send_json_response(200, {"success": True, "id": obs_id})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_delete_observance(self, query):
        try:
            obs_id = query.get('id', [''])[0].strip()
            obs = load_custom_observances()
            filtered = [o for o in obs if o["id"] != obs_id]
            save_custom_observances(filtered)
            CACHE.clear()
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_export_observances(self, query):
        try:
            filepath = query.get('filepath', [''])[0].strip()
            if not filepath:
                self.send_json_response(400, {"error": "filepath parameter is required"})
                return
            
            filepath = os.path.expanduser(filepath)
            
            # Read local custom_observances
            obs = load_custom_observances()
            
            # Write to filepath
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(obs, f, indent=2, ensure_ascii=False)
                
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_import_observances(self, query):
        try:
            filepath = query.get('filepath', [''])[0].strip()
            if not filepath:
                self.send_json_response(400, {"error": "filepath parameter is required"})
                return
            
            filepath = os.path.expanduser(filepath)
            
            if not os.path.exists(filepath):
                self.send_json_response(400, {"error": "file does not exist"})
                return
                
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_obs = json.load(f)
                
            if not isinstance(imported_obs, list):
                self.send_json_response(400, {"error": "invalid format, expected list of observances"})
                return
                
            # Basic validation
            validated = []
            for item in imported_obs:
                if not isinstance(item, dict):
                    continue
                obs_id = item.get("id", "") or str(uuid.uuid4())
                name = item.get("name", "").strip()
                month = item.get("month", "").strip()
                paksha = item.get("paksha", "").strip()
                tithi = item.get("tithi", "").strip()
                system = item.get("system", "amavasyanta").strip()
                g_year = item.get("gregorian_year", None)
                if g_year is not None and str(g_year).strip() != "":
                    try:
                        g_year = int(g_year)
                    except ValueError:
                        g_year = None
                if name and month and paksha and tithi:
                    validated.append({
                        "id": obs_id,
                        "name": name,
                        "month": month,
                        "paksha": paksha,
                        "tithi": tithi,
                        "system": system,
                        "gregorian_year": g_year
                    })
                    
            if not validated:
                self.send_json_response(400, {"error": "no valid observances found to import"})
                return
                
            # Merge with existing ones
            existing = load_custom_observances()
            existing_by_key = {f"{o['month']}-{o['paksha']}-{o['tithi']}-{o['name']}-{o.get('system', 'amavasyanta')}": o for o in existing}
            
            for item in validated:
                key = f"{item['month']}-{item['paksha']}-{item['tithi']}-{item['name']}-{item.get('system', 'amavasyanta')}"
                existing_by_key[key] = item
                
            merged_list = list(existing_by_key.values())
            save_custom_observances(merged_list)
            CACHE.clear()
            
            self.send_json_response(200, {"success": True, "count": len(validated)})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_clear_observances(self):
        try:
            save_custom_observances([])
            CACHE.clear()
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_get_reminders(self):
        reminders = load_reminders()
        self.send_json_response(200, reminders)

    def handle_save_reminder(self, query):
        try:
            rem_id = query.get('id', [''])[0].strip()
            title = query.get('title', [''])[0].strip()
            description = query.get('description', [''])[0].strip()
            rem_type = query.get('type', [''])[0].strip()
            params_json = query.get('params', ['{}'])[0].strip()
            time_type = query.get('time_type', ['sunrise'])[0].strip()
            time_offset_mins = int(query.get('time_offset_mins', [0])[0])
            time_exact_str = query.get('time_exact_str', [''])[0].strip()
            enabled = query.get('enabled', ['true'])[0].strip().lower() == 'true'
            
            if not title:
                self.send_json_response(400, {"error": "Title cannot be empty"})
                return
                
            try:
                params = json.loads(params_json)
            except Exception:
                params = {}
                
            reminders = load_reminders()
            
            # Check for duplicate
            for r in reminders:
                if (r["title"].lower() == title.lower() and 
                    r["type"] == rem_type and 
                    json.dumps(r.get("params", {}), sort_keys=True) == json.dumps(params, sort_keys=True)):
                    if not rem_id or r["id"] != rem_id:
                        self.send_json_response(400, {"error": "Duplicate reminder exists!"})
                        return
                        
            if not rem_id:
                rem_id = str(uuid.uuid4())
                reminders.append({
                    "id": rem_id,
                    "title": title,
                    "description": description,
                    "type": rem_type,
                    "params": params,
                    "time_type": time_type,
                    "time_offset_mins": time_offset_mins,
                    "time_exact_str": time_exact_str,
                    "enabled": enabled
                })
            else:
                updated = False
                for r in reminders:
                    if r["id"] == rem_id:
                        r["title"] = title
                        r["description"] = description
                        r["type"] = rem_type
                        r["params"] = params
                        r["time_type"] = time_type
                        r["time_offset_mins"] = time_offset_mins
                        r["time_exact_str"] = time_exact_str
                        r["enabled"] = enabled
                        updated = True
                        break
                if not updated:
                    reminders.append({
                        "id": rem_id,
                        "title": title,
                        "description": description,
                        "type": rem_type,
                        "params": params,
                        "time_type": time_type,
                        "time_offset_mins": time_offset_mins,
                        "time_exact_str": time_exact_str,
                        "enabled": enabled
                    })
            save_reminders(reminders)
            reminder_wakeup_event.set()
            self.send_json_response(200, {"success": True, "id": rem_id})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_delete_reminder(self, query):
        try:
            rem_id = query.get('id', [''])[0].strip()
            reminders = load_reminders()
            filtered = [r for r in reminders if r["id"] != rem_id]
            save_reminders(filtered)
            reminder_wakeup_event.set()
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_clear_reminders(self):
        try:
            save_reminders([])
            reminder_wakeup_event.set()
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_import_reminders(self, query):
        try:
            filepath = query.get('filepath', [''])[0].strip()
            if not filepath:
                self.send_json_response(400, {"error": "filepath parameter is required"})
                return
                
            filepath = os.path.expanduser(filepath)
            if not os.path.exists(filepath):
                self.send_json_response(400, {"error": "file does not exist"})
                return
                
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_rems = json.load(f)
                
            if not isinstance(imported_rems, list):
                self.send_json_response(400, {"error": "invalid format, expected list of reminders"})
                return
                
            validated = []
            for item in imported_rems:
                if not isinstance(item, dict):
                    continue
                rem_id = item.get("id", "") or str(uuid.uuid4())
                title = item.get("title", "").strip()
                description = item.get("description", "").strip()
                rem_type = item.get("type", "").strip()
                params = item.get("params", {})
                time_type = item.get("time_type", "sunrise").strip()
                time_offset_mins = int(item.get("time_offset_mins", 0))
                time_exact_str = item.get("time_exact_str", "").strip()
                enabled = item.get("enabled", True)
                
                if title and rem_type:
                    validated.append({
                        "id": rem_id,
                        "title": title,
                        "description": description,
                        "type": rem_type,
                        "params": params,
                        "time_type": time_type,
                        "time_offset_mins": time_offset_mins,
                        "time_exact_str": time_exact_str,
                        "enabled": enabled
                    })
                    
            if not validated:
                self.send_json_response(400, {"error": "no valid reminders found to import"})
                return
                
            existing = load_reminders()
            existing_by_key = {}
            for r in existing:
                key = f"{r['title']}-{r['type']}-{json.dumps(r.get('params',{}), sort_keys=True)}"
                existing_by_key[key] = r
                
            for item in validated:
                key = f"{item['title']}-{item['type']}-{json.dumps(item.get('params',{}), sort_keys=True)}"
                existing_by_key[key] = item
                
            save_reminders(list(existing_by_key.values()))
            reminder_wakeup_event.set()
            self.send_json_response(200, {"success": True, "count": len(validated)})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_export_reminders(self, query):
        try:
            filepath = query.get('filepath', [''])[0].strip()
            if not filepath:
                self.send_json_response(400, {"error": "filepath parameter is required"})
                return
                
            filepath = os.path.expanduser(filepath)
            reminders = load_reminders()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, indent=2, ensure_ascii=False)
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_evaluate_reminders(self, query):
        try:
            date_str = query.get('date', [None])[0]
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            calendar_system = query.get('calendar_system', ['shaka'])[0]
            month_system = query.get('month_system', ['amavasyanta'])[0]
            lang = query.get('lang', ['en'])[0]
            
            if not date_str:
                now_utc = datetime.datetime.now(datetime.timezone.utc)
                now_local = now_utc + datetime.timedelta(hours=tz)
                date_str = now_local.strftime("%Y-%m-%d")
                
            parts = date_str.split("-")
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            
            astro = Kalachakra.calculate_panchanga(
                y, m, d, tz, lat, lon, alt,
                calendar_system=calendar_system, month_system=month_system, lang=lang
            )
            
            custom_obs = load_all_observances()
            festivals = Kalotsavachakra.calculate_festivals(
                astro, tz, custom_obs, festival_rule="vaishnava", lang=lang
            )
            
            reminders = load_reminders()
            enabled_reminders = [r for r in reminders if r.get("enabled", True)]
            
            matched = Kalotsavachakra.evaluate_reminders(astro, festivals, enabled_reminders, lang)
            self.send_json_response(200, matched)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def send_json_response(self, status, data):
        if isinstance(data, dict):
            if "error" in data:
                data["success"] = False
                data["message"] = data["error"]
            elif status == 200:
                if "success" not in data:
                    data["success"] = True
                if "message" not in data:
                    data["message"] = "Success"
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def run(port=8642):
    ensure_config_exists()
    t = threading.Thread(target=reminder_daemon_loop, daemon=True)
    t.start()
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, KalasetuRequestHandler)
    logger.info(f"Kalasetu API daemon listening on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    logger.info("Service stopped.")


if __name__ == '__main__':
    port = 8642
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run(port)
