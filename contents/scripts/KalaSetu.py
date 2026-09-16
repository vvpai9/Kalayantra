#!/usr/bin/env python3
"""
KalaSetu - Backend Bridge / Local API Service
Exposes local API endpoints, manages local caches, and orchestrates
calls to KalaChakra, KalaUtsavachakra, and KalaKosha.
"""
import sys
import os
import json
import csv
import io
import datetime
import uuid
import threading
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import KalaChakra
import KalaUtsavachakra
import KalaKosha

CONFIG_DIR = os.path.expanduser("~/.config/kalayantra")
CUSTOM_CITIES_PATH = os.path.join(CONFIG_DIR, "custom_cities.json")
CUSTOM_OBSERVANCES_PATH = os.path.join(CONFIG_DIR, "custom_observances.json")
REMINDERS_PATH = os.path.join(CONFIG_DIR, "reminders.json")
NOTIFICATION_CACHE_PATH = os.path.join(CONFIG_DIR, "notification_cache.json")
LAST_COORDS_PATH = os.path.join(CONFIG_DIR, "last_coordinates.json")

reminder_wakeup_event = threading.Event()

# Simple memory cache for API requests
CACHE = {}

# Canonical date format for all API dates (day, range, kundali, hora, muhurta, ...)
DATE_FORMAT = "%d-%m-%Y"

# Columns exported in CSV format (used by /range, /month and /day with format=csv)
CSV_COLUMNS = [
    "date", "vaara", "tithi", "tithi_1", "tithi_2", "paksha", "masa", "masa_idx",
    "nakshatra", "nakshatra_1", "nakshatra_2", "yoga", "karana", "samvatsara",
    "ritu", "ayana", "era_year", "era_name", "shaka_year", "vikram_year", "kali_year",
    "sunrise", "sunset", "moonrise", "moonset", "rahu_kala", "yamaghanta", "gulika",
    "abhijit_muhurta", "ghadi", "festivals", "festival_types",
]


def json_rows_to_csv(rows):
    """Convert a list of panchanga dicts into a CSV string (spreadsheet-friendly)."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for row in rows:
        rdict = row if isinstance(row, dict) else {}
        line = []
        for col in CSV_COLUMNS:
            v = rdict.get(col, "")
            if col == "festivals":
                v = " | ".join(f.get("name", "") for f in v) if isinstance(v, list) else ""
            elif col == "festival_types":
                v = " | ".join(str(f.get("type", "")) for f in v) if isinstance(v, list) else ""
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            line.append("" if v is None else str(v))
        writer.writerow(line)
    return out.getvalue()

import logging

# Set up structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KalaSetu")

class ConfigManager:
    def __init__(self):
        self.lock = threading.RLock()
        self._custom_cities_cache = None
        self._custom_observances_cache = None
        self._all_observances_cache = None
        self._reminders_cache = None
        self._notification_cache = None
        self._last_coords_cache = None
        self._last_mtimes = {}

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

    def _check_and_invalidate_caches(self):
        mtimes_changed = False
        files_to_check = {
            "custom_obs": CUSTOM_OBSERVANCES_PATH,
            "private_obs": os.path.join(CONFIG_DIR, "private", "private_observances.json"),
            "private_tithis": os.path.join(CONFIG_DIR, "private", "private_tithis.json")
        }
        for key, path in files_to_check.items():
            current_mtime = 0.0
            if os.path.exists(path):
                try:
                    current_mtime = os.path.getmtime(path)
                except Exception:
                    pass
            if self._last_mtimes.get(key) != current_mtime:
                self._last_mtimes[key] = current_mtime
                mtimes_changed = True
        
        if mtimes_changed:
            self._custom_observances_cache = None
            self._all_observances_cache = None
            global CACHE
            CACHE.clear()

    def load_custom_observances(self):
        self._check_and_invalidate_caches()
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
                global CACHE
                CACHE.clear()
            except Exception as e:
                logger.error(f"Error saving custom observances: {e}")

    def load_all_observances(self):
        self._check_and_invalidate_caches()
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
            today_str = today.strftime(DATE_FORMAT)
            
            cache = load_notification_cache()
            if cache.get("date") != today_str:
                cache = {"date": today_str, "sent": []}
                save_notification_cache(cache)
                
            reminders = load_reminders()
            enabled_reminders = [r for r in reminders if r.get("enabled", True)]
            
            astro = KalaChakra.calculate_panchanga(
                today.year, today.month, today.day, tz, lat, lon, alt,
                calendar_system=calendar_system, month_system=month_system, lang=lang
            )
            
            custom_obs = load_all_observances()
            festivals = KalaUtsavachakra.calculate_festivals(
                astro, tz, custom_obs, festival_rule="vaishnava", lang=lang
            )
            
            today_candidates = KalaUtsavachakra.evaluate_reminders(astro, festivals, enabled_reminders, lang)
            
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


class KalaSetuRequestHandler(BaseHTTPRequestHandler):
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
        self.dispatch(url.path, query)

    def do_POST(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        length = int(self.headers.get('Content-Length', 0) or 0)
        body = self.rfile.read(length) if length else b''
        if body:
            try:
                payload = json.loads(body.decode('utf-8'))
                if isinstance(payload, dict):
                    query.update({k: (v if isinstance(v, list) else [v]) for k, v in payload.items()})
            except Exception:
                self.send_json_response(400, {"error": "Invalid JSON body"})
                return
        self.dispatch(url.path, query)

    def dispatch(self, path, query):
        endpoints = {
            '/day': self.handle_day,
            '/month': self.handle_month,
            '/range': self.handle_range,
            '/config': self.handle_config,
            '/search_city': self.handle_search_city,
            '/save_custom_city': self.handle_save_city,
            '/get_custom_observances': self.handle_get_observances,
            '/save_custom_observance': self.handle_save_observance,
            '/delete_custom_observance': self.handle_delete_observance,
            '/export_custom_observances': self.handle_export_observances,
            '/import_custom_observances': self.handle_import_observances,
            '/clear_custom_observances': self.handle_clear_observances,
            '/get_reminders': self.handle_get_reminders,
            '/save_reminder': self.handle_save_reminder,
            '/delete_reminder': self.handle_delete_reminder,
            '/clear_reminders': self.handle_clear_reminders,
            '/import_reminders': self.handle_import_reminders,
            '/export_reminders': self.handle_export_reminders,
            '/evaluate_reminders': self.handle_evaluate_reminders,
            '/kundali': self.handle_kundali,
            '/hora': self.handle_hora,
            '/muhurta': self.handle_muhurta,
            '/ashtakoota': self.handle_ashtakoota,
            '/analysis': self.handle_analysis,
            '/gochara': self.handle_gochara,
            '/bodha': self.handle_bodha,
            '/api/v1/bodha': self.handle_bodha,
            '/medha': self.handle_medha,
            '/api/v1/medha': self.handle_medha,
            '/vidya': self.handle_vidya,
            '/api/v1/vidya': self.handle_vidya,
            '/launch_app': self.handle_launch_app,
            '/system_info': self.handle_system_info,
            '/openapi.json': self.handle_openapi,
            '/docs': self.handle_docs,
        }
        handler = endpoints.get(path)
        if handler:
            handler(query)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_system_info(self, query=None):
        import platform
        info = {
            "architecture": platform.machine(),
            "system": platform.system(),
            "processor": platform.processor(),
        }
        self.send_json_response(200, info)

    def handle_config(self, query=None):
        try:
            coords = load_last_coordinates() or {}
            config = {
                "lat": coords.get("lat", 23.1765),
                "lon": coords.get("lon", 75.7885),
                "alt": coords.get("alt", 0.0),
                "tz": coords.get("tz", 5.5),
                "lang": coords.get("lang", "en"),
                "calendar_system": coords.get("calendar_system", "shaka"),
                "month_system": coords.get("month_system", "amavasyanta"),
                "festival_rule": coords.get("festival_rule", "vaishnava"),
                "tithi_mode": coords.get("tithi_mode", "traditional"),
                "ayanamsa": coords.get("ayanamsa", "lahiri"),
                "city": coords.get("city", ""),
            }
            self.send_json_response(200, config)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_day(self, query):
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
                date_str = dt.strftime(DATE_FORMAT)
                
            tithi_mode = query.get('tithi_mode', ['traditional'])[0]
            calendar_system = query.get('calendar_system', ['shaka'])[0]
            month_system = query.get('month_system', ['amavasyanta'])[0]
            festival_rule = query.get('festival_rule', ['vaishnava'])[0]
            lang = query.get('lang', ['en'])[0]
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            detail = query.get('detail', ['false'])[0].lower() in ('true', '1')

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
            today_str = datetime.datetime.now().strftime(DATE_FORMAT)
            is_today = (date_str == today_str)

            clean_query = {k: v for k, v in query.items() if k not in ('_t', '_')}
            cache_key = ("day", json.dumps(clean_query, sort_keys=True))

            if not is_today and cache_key in CACHE:
                self.send_json_response(200, CACHE[cache_key])
                return

            # Compute astronomical data from KalaChakra
            if detail:
                astro_data = KalaChakra.calculate_detailed_panchanga(
                    dt.year, dt.month, dt.day, tz, lat, lon, alt,
                    ayanamsa=ayanamsa, lang=lang,
                )
            else:
                astro_data = KalaChakra.calculate_panchanga(
                    dt.year, dt.month, dt.day, tz, lat, lon, alt,
                    tithi_mode, calendar_system, month_system, lang
                )
            
            # Load custom observances
            custom_obs = load_all_observances()
            
            # Compute festivals from KalaUtsavachakra
            festivals = KalaUtsavachakra.calculate_festivals(
                astro_data, tz, custom_obs, festival_rule, lang
            )
            
            # Merge festivals list into final JSON payload
            astro_data["festivals"] = festivals
            
            # Cache results if it is NOT today
            if not is_today:
                CACHE[cache_key] = astro_data

            fmt = query.get('format', ['json'])[0].lower()
            if fmt == 'csv':
                self.send_csv_response(200, [astro_data])
            else:
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
                astro_data = KalaChakra.calculate_panchanga(
                    year, month, d, tz, lat, lon, alt,
                    tithi_mode, calendar_system, month_system, lang
                )
                festivals = KalaUtsavachakra.calculate_festivals(
                    astro_data, tz, custom_obs, festival_rule, lang
                )
                astro_data["festivals"] = festivals
                days_data.append(astro_data)
                
            CACHE[cache_key] = days_data
            fmt = query.get('format', ['json'])[0].lower()
            if fmt == 'csv':
                self.send_csv_response(200, days_data)
            else:
                self.send_json_response(200, days_data)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_range(self, query):
        clean_query = {k: v for k, v in query.items() if k not in ('_t', '_')}
        cache_key = ("range", json.dumps(clean_query, sort_keys=True))
        if cache_key in CACHE:
            days_data = CACHE[cache_key]
        else:
            try:
                lat = float(query.get('lat', [23.1765])[0])
                lon = float(query.get('lon', [75.7885])[0])
                alt = float(query.get('alt', [0.0])[0])
                tz = float(query.get('tz', [5.5])[0])
                
                now_local = datetime.datetime.now() + datetime.timedelta(hours=tz)
                today_str = now_local.strftime(DATE_FORMAT)
                
                start_str = query.get('start', [None])[0]
                end_str = query.get('end', [None])[0]
                date_str = query.get('date', [None])[0]
                days = query.get('days', [None])[0]
                
                if not start_str:
                    start_str = date_str or today_str
                start_dt = datetime.datetime.strptime(start_str, DATE_FORMAT)
                
                if not end_str:
                    if days:
                        end_dt = start_dt + datetime.timedelta(days=int(days) - 1)
                    else:
                        end_dt = start_dt
                else:
                    end_dt = datetime.datetime.strptime(end_str, DATE_FORMAT)
                    
                if end_dt < start_dt:
                    self.send_json_response(400, {"error": "end must be on or after start"})
                    return
                total_days = (end_dt - start_dt).days + 1
                if total_days > 372:
                    self.send_json_response(400, {"error": "range limited to 372 days at a time"})
                    return

                tithi_mode = query.get('tithi_mode', ['traditional'])[0]
                calendar_system = query.get('calendar_system', ['shaka'])[0]
                month_system = query.get('month_system', ['amavasyanta'])[0]
                festival_rule = query.get('festival_rule', ['vaishnava'])[0]
                lang = query.get('lang', ['en'])[0]

                custom_obs = load_all_observances()
                
                days_data = []
                day = start_dt
                while day <= end_dt:
                    astro_data = KalaChakra.calculate_panchanga(
                        day.year, day.month, day.day, tz, lat, lon, alt,
                        tithi_mode, calendar_system, month_system, lang
                    )
                    festivals = KalaUtsavachakra.calculate_festivals(
                        astro_data, tz, custom_obs, festival_rule, lang
                    )
                    astro_data["festivals"] = festivals
                    days_data.append(astro_data)
                    day += datetime.timedelta(days=1)
                    
                CACHE[cache_key] = days_data
                
            except ValueError:
                self.send_json_response(400, {"error": "dates must be in DD-MM-YYYY format"})
                return
            except Exception as e:
                self.send_json_response(500, {"error": str(e)})
                return
        
        fmt = query.get('format', ['json'])[0].lower()
        if fmt == 'csv':
            self.send_csv_response(200, days_data)
        else:
            self.send_json_response(200, days_data)

    def handle_search_city(self, query):
        q = query.get('q', [''])[0].strip().lower()
        results = []
        
        # Load preset and custom cities
        presets = KalaKosha.BUILTIN_CITIES
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

    def handle_get_observances(self, query=None):
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

    def handle_clear_observances(self, query=None):
        try:
            save_custom_observances([])
            CACHE.clear()
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_get_reminders(self, query=None):
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

    def handle_clear_reminders(self, query=None):
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
                date_str = now_local.strftime(DATE_FORMAT)
                
            parts = date_str.split("-")
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            
            astro = KalaChakra.calculate_panchanga(
                y, m, d, tz, lat, lon, alt,
                calendar_system=calendar_system, month_system=month_system, lang=lang
            )
            
            custom_obs = load_all_observances()
            festivals = KalaUtsavachakra.calculate_festivals(
                astro, tz, custom_obs, festival_rule="vaishnava", lang=lang
            )
            
            body_reminders = query.get('reminders', None)
            if isinstance(body_reminders, list) and body_reminders and isinstance(body_reminders[0], dict):
                reminders = body_reminders
            else:
                reminders = load_reminders()
            enabled_reminders = [r for r in reminders if r.get("enabled", True)]
            
            matched = KalaUtsavachakra.evaluate_reminders(astro, festivals, enabled_reminders, lang)
            self.send_json_response(200, matched)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    @staticmethod
    def person_from_query(query, key):
        """Return a person dict from a POST body (bride/groom dict) or from
        flat query parameters (bride_year, bride_moon_rashi, ...)."""
        obj = query.get(key, [None])[0]
        if isinstance(obj, dict):
            return obj
        p = {}
        for f in ("year", "month", "day", "hour", "minute", "tz",
                  "moon_rashi", "moon_nakshatra", "moon_pada"):
            v = query.get(f"{key}_{f}")
            if v:
                val = v[0]
                if f in ("year", "month", "day", "moon_rashi", "moon_nakshatra", "moon_pada"):
                    try:
                        val = int(val)
                    except (TypeError, ValueError):
                        pass
                elif f in ("hour", "minute", "tz"):
                    try:
                        val = float(val)
                    except (TypeError, ValueError):
                        pass
                p[f] = val
        if "moon_rashi" in p:
            p["rashi"] = p["moon_rashi"]
        if "moon_nakshatra" in p:
            p["nak"] = p["moon_nakshatra"]
        if "moon_pada" in p:
            p["pada"] = p["moon_pada"]
        return p if p else None

    def handle_kundali(self, query):
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
            hour = float(query.get('hour', [12.0])[0])
            minute = float(query.get('minute', [0])[0])
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]
            dasha_depth = int(query.get('dasha_depth', ['3'])[0])

            kd = KalaChakra.calculate_kundali(
                dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                ayanamsa=ayanamsa, lang=lang, dasha_depth=dasha_depth,
            )
            kd["_meta"] = {"date": date_str or dt.strftime(DATE_FORMAT),
                           "hour": hour, "minute": minute, "ayanamsa": ayanamsa}
            self.send_json_response(200, kd)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_analysis(self, query):
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
            hour = float(query.get('hour', [12.0])[0])
            minute = float(query.get('minute', [0])[0])
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]

            dasha_depth = int(query.get('dasha_depth', ['3'])[0])
            kd = KalaChakra.calculate_kundali(
                dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                ayanamsa=ayanamsa, lang=lang, dasha_depth=dasha_depth,
            )
            analysis = KalaChakra.generate_analysis(kd, lang=lang)
            self.send_json_response(200, {"kundali": kd, "analysis": analysis})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_bodha(self, query):
        """Structured Jyotisa reasoning layer (KalaBodha): semantic chart
        representation, drishti, conjunctions, graha yuddhas, statuses,
        yogas, an evidence graph, programmatic answers and birth-time
        sensitivity."""
        try:
            import KalaBodha
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
            hour = float(query.get('hour', [12.0])[0])
            minute = float(query.get('minute', [0])[0])
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]
            dasha_depth = int(query.get('dasha_depth', ['3'])[0])
            sensitivity = query.get('sensitivity', ['false'])[0].lower() in ('true', '1')

            kd = KalaChakra.calculate_kundali(
                dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                ayanamsa=ayanamsa, lang=lang, dasha_depth=dasha_depth,
            )
            bodha = KalaBodha.analyze_chart(kd, lang=lang)
            response = {"kundali": kd, "bodha": bodha}
            if sensitivity:
                response["sensitivity"] = KalaBodha.birth_time_sensitivity(
                    dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                    ayanamsa=ayanamsa, lang=lang)
            self.send_json_response(200, response)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_medha(self, query):
        """KalaMedha — offline AI reading layer over the KalaBodha evidence
        graph.  Returns a deterministic narrative + graha strength rankings +
        programmatic answers.  When *question* is supplied, answers that one
        question.  When *llm=true* and a local Ollama provider is reachable,
        an optional LLM-flavoured reading is appended (it degrades gracefully
        to the rule engine)."""
        try:
            import KalaMedha
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
            hour = float(query.get('hour', [12.0])[0])
            minute = float(query.get('minute', [0])[0])
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]
            dasha_depth = int(query.get('dasha_depth', ['3'])[0])
            question = query.get('question', [None])[0]
            use_llm = query.get('llm', ['false'])[0].lower() in ('true', '1')

            kd = KalaChakra.calculate_kundali(
                dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                ayanamsa=ayanamsa, lang=lang, dasha_depth=dasha_depth,
            )
            response = {"kundali": kd}
            if use_llm:
                response["medha"] = KalaMedha.medha_with_llm(kd, lang=lang)
            else:
                response["medha"] = KalaMedha.medha_analysis(kd, lang=lang)
            if question:
                response["answer"] = KalaMedha.answer_question(question, kd, lang=lang)
            self.send_json_response(200, response)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_vidya(self, query):
        """KalaVidya — the informational knowledge layer.

        Pure data: \"/vidya\" returns the full concept catalog (id, category,
        localized title/summary); add ``category=…`` to filter it. \"/vidya?
        concept=tithi\" returns one full entry (detail, formula, example,
        source, see_also). \"/vidya?q=…\" runs a keyword search. No
        astronomical computation is needed, so any ChartParams style input is
        ignored."""
        try:
            import KalaVidya
            lang = query.get('lang', ['en'])[0]
            concept_ref = query.get('concept', [None])[0]
            if concept_ref is not None:
                entry = KalaVidya.get_concept(concept_ref, lang)
                response = {
                    "concept": entry,
                    "found": entry is not None,
                    "categories": KalaVidya.categories(lang),
                }
                self.send_json_response(200, response)
                return
            q = query.get('q', [None])[0]
            category = query.get('category', [None])[0]
            if q is not None and q.strip():
                results = KalaVidya.search_concepts(q, lang)
                response = {"search": results, "count": len(results),
                            "query": q.strip(), "categories": KalaVidya.categories(lang)}
            else:
                catalog = KalaVidya.concept_catalog(lang, category=category)
                response = {"catalog": catalog, "count": len(catalog),
                            "categories": KalaVidya.categories(lang)}
                if category:
                    response["category"] = category
            self.send_json_response(200, response)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_gochara(self, query):
        """Gochara — current planetary transits against a natal chart.

        Accepts the natal chart parameters (date/hour/minute) like /kundali,
        plus optional *transit_date* / *transit_hour* / *transit_minute* for
        the moment to evaluate. Computes where each transit graha currently
        sits (and what it aspects relative to the natal lagna), special
        transits (Sade Sati, Ashtama Shani, Guru Gochara), upcoming sign
        changes, and tight 1-degree transits conjuncting natal planets.
        """
        try:
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            date_str = query.get('date', [None])[0]
            if date_str:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            else:
                dt = datetime.datetime.now()
            hour = float(query.get('hour', [12.0])[0])
            minute = float(query.get('minute', [0])[0])
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]
            dasha_depth = int(query.get('dasha_depth', ['3'])[0])

            t_date_str = query.get('transit_date', [None])[0]
            if t_date_str:
                t_dt = datetime.datetime.strptime(t_date_str, DATE_FORMAT)
            else:
                t_dt = dt
            t_hour = float(query.get('transit_hour', [t_dt.hour])[0])
            t_minute = float(query.get('transit_minute', [t_dt.minute])[0])

            kd = KalaChakra.calculate_kundali(
                dt.year, dt.month, dt.day, hour, minute, tz, lat, lon, alt,
                ayanamsa=ayanamsa, lang=lang, dasha_depth=dasha_depth,
            )
            gochara = KalaChakra.calculate_gochara(
                kd, t_dt.year, t_dt.month, t_dt.day, t_hour, t_minute,
                tz, lat, lon, lang=lang, ayanamsa=ayanamsa,
            )
            self.send_json_response(200, {"kundali": kd, "gochara": gochara})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_hora(self, query):
        try:
            date_str = query.get('date', [None])[0]
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            lang = query.get('lang', ['en'])[0]
            if not date_str:
                now_local = datetime.datetime.now() + datetime.timedelta(hours=tz)
                dt = now_local
            else:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            data = KalaChakra.calculate_dina_horas(
                dt.year, dt.month, dt.day, tz, lat, lon, alt, lang=lang)
            self.send_json_response(200, data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_muhurta(self, query):
        try:
            date_str = query.get('date', [None])[0]
            lat = float(query.get('lat', [23.1765])[0])
            lon = float(query.get('lon', [75.7885])[0])
            alt = float(query.get('alt', [0.0])[0])
            tz = float(query.get('tz', [5.5])[0])
            lang = query.get('lang', ['en'])[0]
            if not date_str:
                now_local = datetime.datetime.now() + datetime.timedelta(hours=tz)
                dt = now_local
            else:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
            data = KalaChakra.calculate_muhurtas(
                dt.year, dt.month, dt.day, tz, lat, lon, alt, lang=lang)
            self.send_json_response(200, data)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_ashtakoota(self, query):
        try:
            ayanamsa = query.get('ayanamsa', ['lahiri'])[0]
            lang = query.get('lang', ['en'])[0]
            bride = self.person_from_query(query, "bride")
            groom = self.person_from_query(query, "groom")
            if not bride or not groom:
                self.send_json_response(400, {"error": "bride and groom birth data are required "
                                                       "(POST JSON body with bride/groom objects, "
                                                       "or bride_year/bride_... flat params)"})
                return
            result = KalaChakra.calculate_ashtakoota(bride, groom, ayanamsa=ayanamsa, lang=lang)
            self.send_json_response(200, result)
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_launch_app(self, query=None):
        """Launch the standalone KalaYantra desktop app (used by the widget's
        'Open App' button). Inherits the daemon's session environment so the
        window appears on the user's active display."""
        try:
            home = os.path.expanduser("~")
            candidates = [
                os.path.join(home, ".local/share/kalayantra/standalone/kalayantra-app"),
                os.path.join(home, ".local/share/kalayantra/standalone/KalaYantraApp.qml"),
            ]
            launcher = None
            for cand in candidates:
                if os.path.isfile(cand):
                    launcher = cand
                    break
            if launcher is None:
                self.send_json_response(404, {"error": "Standalone app is not installed."})
                return
            subprocess.Popen([launcher],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
            self.send_json_response(200, {"status": "launching", "target": launcher})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_openapi(self, query=None):
        common_params = [
            ("date", "DD-MM-YYYY for /day, /range"),
            ("start", "Range start DD-MM-YYYY"),
            ("end", "Range end DD-MM-YYYY"),
            ("days", "Number of days from start (alternative to end)"),
            ("year", "Year for /month"),
            ("month", "Month (1-12) for /month"),
            ("lat", "Latitude (default 23.1765)"),
            ("lon", "Longitude (default 75.7885)"),
            ("alt", "Altitude in metres (default 0)"),
            ("tz", "UTC offset in hours (default 5.5)"),
            ("tithi_mode", "traditional | current"),
            ("calendar_system", "shaka | vikram | kartak | saura"),
            ("month_system", "amavasyanta | purnimanta"),
            ("festival_rule", "vaishnava | smarta"),
            ("lang", "en | iast | devanagari"),
            ("format", "json | csv"),
        ]
        kundali_params = [
            ("date", "Birth date DD-MM-YYYY"),
            ("hour", "Birth hour (0-23)"),
            ("minute", "Birth minute (0-59)"),
            ("lat", "Birth latitude"),
            ("lon", "Birth longitude"),
            ("alt", "Birth altitude in metres"),
            ("tz", "UTC offset in hours"),
            ("ayanamsa", "lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce | sayana"),
            ("lang", "en | iast | devanagari"),
        ]
        ashtakoota_params = [
            ("bride_year", "Bride birth year (flat params; or pass bride/groom objects in JSON body)"),
            ("bride_month", "Bride birth month"),
            ("bride_day", "Bride birth day"),
            ("bride_hour", "Bride birth hour"),
            ("bride_minute", "Bride birth minute"),
            ("bride_tz", "Bride birth UTC offset"),
            ("bride_moon_rashi", "Bride moon rashi (0-11) as alternative to birth data"),
            ("bride_moon_nakshatra", "Bride moon nakshatra (0-26)"),
            ("bride_moon_pada", "Bride moon pada (1-4)"),
            ("groom_year", "Groom birth year (or groom_* equivalents)"),
            ("groom_month", "Groom birth month"),
            ("groom_day", "Groom birth day"),
            ("groom_hour", "Groom birth hour"),
            ("groom_minute", "Groom birth minute"),
            ("groom_tz", "Groom birth UTC offset"),
            ("groom_moon_rashi", "Groom moon rashi (0-11)"),
            ("groom_moon_nakshatra", "Groom moon nakshatra (0-26)"),
            ("groom_moon_pada", "Groom moon pada (1-4)"),
            ("ayanamsa", "lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce"),
            ("lang", "en | iast | devanagari"),
        ]

        def build_op(summary, params, desc=""):
            op = {
                "summary": summary,
                "description": desc,
                "parameters": [
                    {"name": n, "in": "query", "required": False, "schema": {"type": "string"}, "description": d}
                    for n, d in params
                ],
                "responses": {
                    "200": {"description": "OK"},
                    "400": {"description": "Bad request"},
                    "500": {"description": "Server error"},
                },
            }
            return op

        paths = {}
        for path, summary, params, desc, allow_post in [
            ("/day", "Panchanga and festivals for one day", common_params, "Full panchanga JSON/CSV for a single date; requires date. Add detail=true and ayanamsa=... for the Detailed Panchang report (rising graha positions, dina horas and muhurtas).", True),
            ("/month", "Panchanga and festivals for a month", common_params, "List of daily panchanga records for year+month.", True),
            ("/range", "Panchanga and festivals for a date range", common_params, "Bulk range endpoint ideal for spreadsheets; use start & end or date & days. Cap 372 days.", True),
            ("/search_city", "Search built-in and custom cities", [("q", "City name fragment")], "Returns city list with lat/lon/tz/alt.", False),
            ("/save_custom_city", "Add a custom city", [("name", ""), ("lat", ""), ("lon", ""), ("tz", ""), ("alt", "")], "Register a user city in the custom registry.", False),
            ("/launch_app", "Launch the standalone desktop app", [], "Opens the KalaYantra standalone application window.", False),
            ("/kundali", "Natal chart (D1/D3/D9 + other vargas, Vimshottari dashas)", kundali_params, "Birth-chart engine: all-nine-graha positions, dignity, combustion, whole-sign houses, vargas and mahadasha sequence.", True),
            ("/hora", "Dina hora (24 Chaldean hours)", common_params, "The 12 day horas from sunrise and 12 night horas from sunset with their lords.", True),
            ("/muhurta", "Day/night muhurtas with status", common_params, "15 day and 15 night muhurtas classified as Abhijit/Auspicious/Neutral/Inauspicious (Rahu, Yama, Gulika overlap).", True),
            ("/ashtakoota", "Ashtakoota (Guna Milan) compatibility", ashtakoota_params, "Eight-fold compatibility of bride and groom from their Moon rashi/nakshatra/pada or birth data, with Nadi and Bhakoot dosha cancellations.", True),
            ("/analysis", "Offline rule-based chart analysis", kundali_params, "Kundali plus heuristic analysis: lagna-lord strength, dignity, combustion/retrograde, Mangal Dosha, Navamsa checks. Runs fully offline.", True),
            ("/gochara", "Planetary transits against a natal chart (Gochara)", kundali_params + [("transit_date", "DD-MM-YYYY moment to evaluate (defaults to natal date)"), ("transit_hour", "Hour for the transit moment"), ("transit_minute", "Minute for the transit moment")], "Transit positions of all nine grahas with house/aspect mapping from the natal lagna, special transit yogas (Sade Sati, Ashtama Shani, Guru Gochara), upcoming sign changes and tight conjunctions with natal planets.", True),
            ("/bodha", "Structured Jyotisa reasoning (KalaBodha)", kundali_params + [("sensitivity", "true to include birth-time sensitivity report")], "Semantic chart representation with graha drishti, conjunctions, graha yuddhas, status markers (Uccha/Neecha/Asta/Vakri/...), structured yogas, an evidence graph, programmatic chart answers and optional birth-time sensitivity.", True),
            ("/api/v1/bodha", "Structured Jyotisa reasoning (KalaBodha, versioned alias)", kundali_params + [("sensitivity", "true to include birth-time sensitivity report")], "Versioned alias of /bodha.", True),
            ("/medha", "Offline AI reading (KalaMedha)", kundali_params + [("question", "optional natural-language question to answer from the chart"), ("llm", "true to try the optional local LLM hook")], "Deterministic narrative (lagna, grahas, yogas, dasha) + explainable per-graha strength rankings + programmatic answers derived from the KalaBodha evidence graph. No external AI required; llm=true is an optional enhancement when a local Ollama provider is reachable.", True),
            ("/api/v1/medha", "Offline AI reading (KalaMedha, versioned alias)", kundali_params + [("question", "optional natural-language question to answer from the chart"), ("llm", "true to try the optional local LLM hook")], "Versioned alias of /medha.", True),
            ("/vidya", "Informational knowledge layer (KalaVidya)", [("concept", "concept id or title to fetch in full (e.g. tithi)"), ("category", "filter the catalog by category slug"), ("q", "keyword search across titles/summaries"), ("lang", "display language")], "Serves the KalaVidya knowledge base: the full concept catalog, a single detailed concept (meaning, formula the engine uses, worked example, classical source, cross-references) or ranked search results — pure data, no chart computation.", True),
            ("/api/v1/vidya", "Informational knowledge layer (KalaVidya, versioned alias)", [("concept", "concept id or title to fetch in full"), ("category", "filter the catalog by category slug"), ("q", "keyword search"), ("lang", "display language")], "Versioned alias of /vidya.", True),
            ("/get_custom_observances", "List custom observances", [], "Returns all user-defined tithi observances.", False),
            ("/save_custom_observance", "Create/update custom observance", [("name", ""), ("month", ""), ("paksha", "Shukla|Krishna"), ("tithi", ""), ("system", "amavasyanta|purnimanta"), ("gregorian_year", ""), ("id", "uuid to update")], "Save a custom lunar observance.", False),
            ("/delete_custom_observance", "Delete custom observance", [("id", "Obs id")], "Remove an observance.", False),
            ("/export_custom_observances", "Export custom observances", [], "Export all custom observances as JSON.", False),
            ("/import_custom_observances", "Import custom observances", [], "Import custom observances from JSON body.", False),
            ("/clear_custom_observances", "Clear all custom observances", [], "Remove all custom observances.", False),
            ("/get_reminders", "List reminders", [], "Return all reminders.", False),
            ("/save_reminder", "Create/update reminder", [("id", ""), ("title", ""), ("type", "tithi|paksha_tithi|masa_paksha_tithi|nakshatra|vara_tithi|sankranti|festival"), ("params", "JSON string"), ("time_type", "sunrise|sunset|noon|exact"), ("time_offset_mins", "0"), ("time_exact_str", "HH:MM"), ("enabled", "true|false")], "Save a reminder.", False),
            ("/delete_reminder", "Delete reminder", [("id", "Reminder id")], "Remove a reminder.", False),
            ("/clear_reminders", "Clear all reminders", [], "Remove all reminders.", False),
            ("/import_reminders", "Import reminders", [], "Import reminders from JSON body.", False),
            ("/export_reminders", "Export reminders", [], "Export all reminders as JSON.", False),
            ("/evaluate_reminders", "Evaluate reminders for a date", common_params, "Return reminders matching a date.", True),
            ("/system_info", "Runtime system information", [], "platform.machine() etc.", True),
            ("/config", "Saved coordinates and calendar settings", [], "Last used location and engine settings; used by the standalone app to adopt widget configuration.", False),
        ]:
            item = {"get": build_op(summary, params, desc)}
            if allow_post:
                item["post"] = build_op(summary, params, desc)
            paths[path] = item
        paths["/openapi.json"] = {"get": build_op("OpenAPI specification", [], "This document.")}
        paths["/docs"] = {"get": build_op("Human-readable API documentation", [], "HTML documentation page.")}

        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "KalaYantra API",
                "version": "2.2.0",
                "description": "Local Panchanga & Festival engine exposing tithi, paksha, masa, nakshatra, festivals, kundali (natal chart), hora, muhurta, ashtakoota, an offline rule-based analysis and the KalaBodha structured Jyotisa reasoning layer. Ideal for spreadsheets (Excel/Sheets), Word, and PowerPoint via the /range?format=csv endpoint or direct HTTP POST."
            },
            "servers": [{"url": "http://127.0.0.1:8642"}],
            "paths": paths,
        }
        self.send_json_response(200, spec)

    def handle_docs(self, query=None):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>KalaYantra API</title>
<style>
body{font-family:system-ui,Segoe UI,Roboto,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222;line-height:1.55}
h1{border-bottom:3px solid #2ecc71;padding-bottom:.4rem}
code{background:#f0f0f0;padding:.1rem .35rem;border-radius:4px;font-size:.92em}
pre{background:#1e1e2e;color:#cdd6f4;padding:1rem;border-radius:8px;overflow-x:auto;font-size:.9em}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:.45rem .6rem;border-bottom:1px solid #ddd}
th{background:#f6f6f6}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:99px;font-size:.75rem;font-weight:600}
.get{background:#e8f5e9;color:#1b5e20}.post{background:#e3f2fd;color:#0d47a1}
</style>
</head>
<body>
<h1>KalaYantra — Local Panchanga API</h1>
<p>KalaSetu exposes the full astro engine on <code>http://127.0.0.1:8642</code>.
It serves JSON by default, and <b>CSV</b> whenever <code>format=csv</code> is added — perfect for
Excel, LibreOffice Calc, Google Sheets (Power Query / API connector), Word mail-merge and PowerPoint tables.</p>

<h2>Spreadsheet quick start</h2>
<p>Fetch a whole year for your city as CSV:</p>
<pre>GET http://127.0.0.1:8642/range?start=01-01-2026&end=31-12-2026&days=365&lat=16.3067&lon=80.4365&alt=0&tz=5.5&format=csv</pre>
<p>In Excel: <b>Data → From Web (Power Query)</b>, paste the URL above, and the table will load with one row per day
(<code>tithi</code>, <code>masa</code>, <code>nakshatra</code>, <code>festivals</code>, and more).</p>

<h2>Endpoints</h2>
<table>
<tr><th>Endpoint</th><th>Description</th></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/day</code></td><td>One day: pass <code>date=DD-MM-YYYY</code>. Add <code>detail=true</code> for the Detailed Panchang report (graha positions, horas, muhurtas)</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/month</code></td><td>One month: pass <code>year</code> &amp; <code>month</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/range</code></td><td>Date range (≤372 days): <code>start</code>/<code>end</code> or <code>date</code>/<code>days</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/kundali</code></td><td>Natal chart: <code>date</code>, <code>hour</code>, <code>minute</code>, <code>ayanamsa</code>, <code>lat</code>, <code>lon</code>, <code>tz</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/hora</code></td><td>24 dina horas (Chaldean hourly lords)</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/muhurta</code></td><td>30 day/night muhurtas with Abhijit and dosha status</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/ashtakoota</code></td><td>36-guna compatibility from <code>bride</code>/<code>groom</code> birth objects</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/analysis</code></td><td>Offline rule-based chart analysis (kundali + highlights)</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/gochara</code></td><td>Planetary transits (Gochara) against a natal chart: Sade Sati, Ashtama Shani, Guru Gochara, sign changes, tight transits</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/bodha</code></td><td>KalaBodha structured Jyotiṣa reasoning: drishti, conjunctions, graha yuddhas, statuses (Uccha/Neecha/Asta/Vakri…), yogas, evidence graph, programmatic answers, and <code>sensitivity=true</code> birth-time report</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/api/v1/bodha</code></td><td>Versioned alias of <code>/bodha</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/medha</code></td><td>KalaMedha offline AI reading: Lagna/graha/yoga/dasha narrative, explainable per-graha strength rankings and programmatic answers over the KalaBodha evidence graph; optional <code>question=…</code> and <code>llm=true</code> (local Ollama) hooks</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/api/v1/medha</code></td><td>Versioned alias of <code>/medha</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/vidya</code></td><td>KalaVidya informational layer: full concept catalog, a single detailed concept (<code>concept=…</code>), or keyword search (<code>q=…</code>) — meaning, engine formula, worked example and classical source</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/api/v1/vidya</code></td><td>Versioned alias of <code>/vidya</code></td></tr>
<tr><td><span class="badge get">GET</span> <code>/search_city</code></td><td>Find built-in city: <code>q=ujjain</code></td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/save_custom_city</code></td><td>Add a custom city to the user registry</td></tr>
<tr><td><span class="badge get">GET</span> <code>/get_custom_observances</code></td><td>My Tithis list</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/save_custom_observance</code></td><td>Create/update a custom lunar observance</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/delete_custom_observance</code></td><td>Delete a custom observance</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/export_custom_observances</code></td><td>Export all custom observances as JSON</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/import_custom_observances</code></td><td>Import custom observances from JSON body</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/clear_custom_observances</code></td><td>Remove all custom observances</td></tr>
<tr><td><span class="badge get">GET</span> <code>/get_reminders</code></td><td>Reminders list</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/save_reminder</code></td><td>Create/update a reminder</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/delete_reminder</code></td><td>Delete a reminder</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/clear_reminders</code></td><td>Remove all reminders</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/import_reminders</code></td><td>Import reminders from JSON body</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/export_reminders</code></td><td>Export all reminders as JSON</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/evaluate_reminders</code></td><td>Reminders matching a date</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/launch_app</code></td><td>Open the standalone KalaYantra desktop app</td></tr>
<tr><td><span class="badge get">GET</span> <span class="badge post">POST</span> <code>/system_info</code></td><td>Runtime info</td></tr>
<tr><td><span class="badge get">GET</span> <code>/config</code></td><td>Saved coordinates &amp; settings (used by the standalone app)</td></tr>
<tr><td><span class="badge get">GET</span> <code>/openapi.json</code></td><td>OpenAPI 3.0 spec (for API-first clients)</td></tr>
</table>

<h2>Query parameters (all endpoints)</h2>
<table>
<tr><th>Param</th><th>Default</th><th>Meaning</th></tr>
<tr><td><code>lat</code>, <code>lon</code>, <code>alt</code></td><td>23.1765, 75.7885, 0</td><td>Observation location (Ujjain default)</td></tr>
<tr><td><code>tz</code></td><td>5.5</td><td>UTC offset in hours</td></tr>
<tr><td><code>tithi_mode</code></td><td>traditional</td><td><code>traditional</code> (Udaya) or <code>current</code> (live)</td></tr>
<tr><td><code>calendar_system</code></td><td>shaka</td><td><code>shaka</code>, <code>vikram</code>, <code>kartak</code>, <code>saura</code></td></tr>
<tr><td><code>month_system</code></td><td>amavasyanta</td><td>amavasyanta or purnimanta</td></tr>
<tr><td><code>festival_rule</code></td><td>vaishnava</td><td>vaishnava or smarta Ekadashi handling</td></tr>
<tr><td><code>lang</code></td><td>en</td><td>en, iast, devanagari</td></tr>
<tr><td><code>format</code></td><td>json</td><td><code>json</code> or <code>csv</code> (spreadsheet-friendly, UTF-8 BOM)</td></tr>
<tr><td><code>ayanamsa</code></td><td>lahiri</td><td>lahiri, raman, krishnamurti, true_citra, fagan_bradley, deluce, or <code>sayana</code> (tropical)</td></tr>
<tr><td><code>detail</code></td><td>false</td><td><code>true</code> on <code>/day</code> for the Detailed Panchang report</td></tr>
</table>

<h2>JSON POST</h2>
<p>Any endpoint also accepts a JSON body with the same parameter names, e.g.</p>
<pre>POST /range
{"start": "01-01-2026", "end": "31-12-2026", "lat": 16.3067, "lon": 80.4365, "tz": 5.5, "format": "csv"}

POST /ashtakoota
{"bride": {"year": 1990, "month": 6, "day": 15, "hour": 10, "minute": 30, "tz": 5.5},
 "groom": {"year": 1992, "month": 3, "day": 8,  "hour": 16, "minute": 45, "tz": 5.5}}

POST /kundali
{"date": "15-06-1990", "hour": 10, "minute": 30, "lat": 13.0827, "lon": 80.2707,
 "tz": 5.5, "ayanamsa": "raman"}</pre>

<h2>OpenAPI</h2>
<p>Machine-readable contract: <a href="/openapi.json">/openapi.json</a></p>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_csv_response(self, status, rows):
        data = json_rows_to_csv(rows)
        self.send_response(status)
        self.send_header('Content-Type', 'text/csv; charset=utf-8')
        self.send_header('Content-Disposition', 'attachment; filename="kalayantra.csv"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data.encode('utf-8-sig'))

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
    httpd = HTTPServer(server_address, KalaSetuRequestHandler)
    logger.info(f"KalaSetu API daemon listening on port {port}...")
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
