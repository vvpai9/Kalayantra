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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import Kalachakra
import Kalotsavachakra
import Kalakosha

CONFIG_DIR = os.path.expanduser("~/.config/kalayantra")
CUSTOM_CITIES_PATH = os.path.join(CONFIG_DIR, "custom_cities.json")
CUSTOM_OBSERVANCES_PATH = os.path.join(CONFIG_DIR, "custom_observances.json")

# Simple memory cache for API requests
CACHE = {}

def ensure_config_exists():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CUSTOM_CITIES_PATH):
        with open(CUSTOM_CITIES_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(CUSTOM_OBSERVANCES_PATH):
        with open(CUSTOM_OBSERVANCES_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_custom_cities():
    ensure_config_exists()
    try:
        with open(CUSTOM_CITIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_custom_cities(cities):
    ensure_config_exists()
    try:
        with open(CUSTOM_CITIES_PATH, "w", encoding="utf-8") as f:
            json.dump(cities, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving custom cities:", e)


def load_custom_observances():
    ensure_config_exists()
    try:
        with open(CUSTOM_OBSERVANCES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_custom_observances(observances):
    ensure_config_exists()
    try:
        with open(CUSTOM_OBSERVANCES_PATH, "w", encoding="utf-8") as f:
            json.dump(observances, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving custom observances:", e)


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
        else:
            self.send_response(404)
            self.end_headers()

    def handle_day(self, query):
        cache_key = ("day", json.dumps(query, sort_keys=True))
        if cache_key in CACHE:
            self.send_json_response(200, CACHE[cache_key])
            return
            
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
                
            tithi_mode = query.get('tithi_mode', ['traditional'])[0]
            calendar_system = query.get('calendar_system', ['shaka'])[0]
            month_system = query.get('month_system', ['amavasyanta'])[0]
            festival_rule = query.get('festival_rule', ['vaishnava'])[0]
            lang = query.get('lang', ['en'])[0]
            
            # Compute astronomical data from Kalachakra
            astro_data = Kalachakra.calculate_panchanga(
                dt.year, dt.month, dt.day, tz, lat, lon, alt,
                tithi_mode, calendar_system, month_system, lang
            )
            
            # Load custom observances
            custom_obs = load_custom_observances()
            
            # Compute festivals from Kalotsavachakra
            festivals = Kalotsavachakra.calculate_festivals(
                astro_data, tz, custom_obs, festival_rule, lang
            )
            
            # Merge festivals list into final JSON payload
            astro_data["festivals"] = festivals
            
            # Cache results
            CACHE[cache_key] = astro_data
            self.send_json_response(200, astro_data)
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_month(self, query):
        cache_key = ("month", json.dumps(query, sort_keys=True))
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
            
            custom_obs = load_custom_observances()
            
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
            
            if not name:
                self.send_json_response(400, {"error": "Name cannot be empty"})
                return
                
            obs = load_custom_observances()
            if not obs_id:
                obs_id = str(uuid.uuid4())
                obs.append({
                    "id": obs_id,
                    "name": name,
                    "month": month,
                    "paksha": paksha,
                    "tithi": tithi
                })
            else:
                updated = False
                for o in obs:
                    if o["id"] == obs_id:
                        o["name"] = name
                        o["month"] = month
                        o["paksha"] = paksha
                        o["tithi"] = tithi
                        updated = True
                        break
                if not updated:
                    obs.append({
                        "id": obs_id,
                        "name": name,
                        "month": month,
                        "paksha": paksha,
                        "tithi": tithi
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
                if name and month and paksha and tithi:
                    validated.append({
                        "id": obs_id,
                        "name": name,
                        "month": month,
                        "paksha": paksha,
                        "tithi": tithi
                    })
                    
            if not validated:
                self.send_json_response(400, {"error": "no valid observances found to import"})
                return
                
            # Merge with existing ones
            existing = load_custom_observances()
            existing_by_key = {f"{o['month']}-{o['paksha']}-{o['tithi']}-{o['name']}": o for o in existing}
            
            for item in validated:
                key = f"{item['month']}-{item['paksha']}-{item['tithi']}-{item['name']}"
                existing_by_key[key] = item
                
            merged_list = list(existing_by_key.values())
            save_custom_observances(merged_list)
            CACHE.clear()
            
            self.send_json_response(200, {"success": True, "count": len(validated)})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def send_json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def run(port=8642):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, KalasetuRequestHandler)
    print(f"Kalasetu API daemon listening on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Service stopped.")

if __name__ == '__main__':
    port = 8642
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run(port)
