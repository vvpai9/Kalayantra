#!/usr/bin/env python3
"""
kalayantra-cli - Command-line interface for the Kālayantra Panchanga engine.

Queries the local KalaSetu daemon (http://127.0.0.1:8642) when it is running and
otherwise falls back to computing values directly. Output is JSON or CSV, making
it convenient for scripts, cron jobs, Excel/VBA, Word mail-merge and import into
spreadsheets.

Examples:
    kalayantra-cli.py day  --date 28-08-2026
    kalayantra-cli.py range --start 01-01-2026 --end 31-12-2026 --format csv --output year.csv
    kalayantra-cli.py festivals --start 01-01-2026 --days 365 --festival-rule vaishnava --format csv
    kalayantra-cli.py search-city --q ujjain
    kalayantra-cli.py gochara --date 15-06-1990 --hour 10 --minute 30 --transit-date 12-09-2026 --lat 13.0827 --lon 80.2707 --tz 5.5 --direct
    kalayantra-cli.py medha --date 15-06-1990 --hour 10 --minute 30 --lat 13.0827 --lon 80.2707 --tz 5.5 --question "Why is Guru strong?" --direct
"""
import sys
import os
import json
import datetime
import argparse
import urllib.request
import urllib.parse
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import KalaChakra
import KalaUtsavachakra
import KalaKosha
from KalaSetu import json_rows_to_csv

DEFAULT_PORT = 8642

DATE_FORMAT = "%d-%m-%Y"


def build_opts(args):
    return {
        "tithi_mode": args.tithi_mode,
        "calendar_system": args.calendar_system,
        "month_system": args.month_system,
        "festival_rule": args.festival_rule,
        "lang": args.lang,
    }


def query_server(port, path, params):
    qs = urllib.parse.urlencode(params)
    url = "http://127.0.0.1:{}{}?{}".format(port, path, qs)
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def compute_day(date_obj, args):
    opts = build_opts(args)
    astro = KalaChakra.calculate_panchanga(
        date_obj.year, date_obj.month, date_obj.day, args.tz, args.lat, args.lon, args.alt,
        opts["tithi_mode"], opts["calendar_system"], opts["month_system"], opts["lang"],
    )
    festivals = KalaUtsavachakra.calculate_festivals(
        astro, args.tz, None, opts["festival_rule"], opts["lang"]
    )
    astro["festivals"] = festivals
    return astro


def compute_range(start, end, args):
    days_data = []
    day = start
    while day <= end:
        days_data.append(compute_day(day, args))
        day += datetime.timedelta(days=1)
    return days_data


def emit(data, args):
    if args.format == "csv":
        text = json_rows_to_csv(data if isinstance(data, list) else [data])
    else:
        text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("Wrote {} to {}".format(("CSV" if args.format == "csv" else "JSON"), args.output))
    else:
        sys.stdout.write(text + "\n")


def cmd_day(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/day", params)), args)
            return
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", "replace")
            print("Server error {}: {}".format(e.code, err), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_day(date_obj, args), args)
    return 0


def cmd_month(args):
    start = datetime.date(args.year, args.month, 1)
    if args.month == 12:
        end = datetime.date(args.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end = datetime.date(args.year, args.month + 1, 1) - datetime.timedelta(days=1)
    if not args.direct:
        try:
            params = {"year": str(args.year), "month": str(args.month)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/month", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_range(start, end, args), args)
    return 0


def cmd_range(args):
    start = datetime.datetime.strptime(args.start, DATE_FORMAT).date()
    if args.end:
        end = datetime.datetime.strptime(args.end, DATE_FORMAT).date()
    else:
        end = start + datetime.timedelta(days=args.days - 1)
    if end < start:
        start, end = end, start
    if (end - start).days + 1 > 372:
        print("Range limited to 372 days at a time.", file=sys.stderr)
        return 1
    if not args.direct:
        try:
            params = {"start": start.strftime(DATE_FORMAT), "end": end.strftime(DATE_FORMAT)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            payload = query_server(args.port, "/range", params)
            emit(json.loads(payload), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_range(start, end, args), args)
    return 0


def cmd_festivals(args):
    start = datetime.datetime.strptime(args.start, DATE_FORMAT).date()
    if args.end:
        end = datetime.datetime.strptime(args.end, DATE_FORMAT).date()
    else:
        end = start + datetime.timedelta(days=args.days - 1)
    rows = compute_range(start, end, args)
    festival_days = [row for row in rows if row.get("festivals")]
    if args.format == "csv":
        emit(festival_days, args)
    else:
        emit([{"date": row["date"], "festivals": [f["name"] for f in row["festivals"]]} for row in festival_days], args)
    return 0


def cmd_search_city(args):
    q = args.q.lower()
    if not args.direct:
        try:
            emit(json.loads(query_server(args.port, "/search_city", {"q": args.q})), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    results = [c for c in KalaKosha.BUILTIN_CITIES if q in c["name"].lower()]
    emit(results[:15], args)
    return 0


def cmd_system_info(args):
    import platform
    info = {
        "architecture": platform.machine(),
        "system": platform.system(),
        "processor": platform.processor(),
    }
    emit(info, args)
    return 0


def cmd_bodha(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            if getattr(args, "sensitivity", False):
                params["sensitivity"] = "true"
            emit(json.loads(query_server(args.port, "/bodha", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    import KalaBodha
    bodha = KalaBodha.analyze_chart(kd, lang=args.lang)
    response = {"kundali": kd, "bodha": bodha}
    if getattr(args, "sensitivity", False):
        response["sensitivity"] = KalaBodha.birth_time_sensitivity(
            date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
            args.tz, args.lat, args.lon, args.alt,
            ayanamsa=args.ayanamsa, lang=args.lang)
    emit(response, args)
    return 0


def cmd_medha(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour),
                      "minute": str(args.minute), "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            if getattr(args, "question", None):
                params["question"] = args.question
            if getattr(args, "llm", False):
                params["llm"] = "true"
            emit(json.loads(query_server(args.port, "/medha", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")),
                  file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    import KalaMedha
    response = {"kundali": kd}
    if getattr(args, "llm", False):
        response["medha"] = KalaMedha.medha_with_llm(kd, lang=args.lang)
    else:
        response["medha"] = KalaMedha.medha_analysis(kd, lang=args.lang)
    if getattr(args, "question", None):
        response["answer"] = KalaMedha.answer_question(args.question, kd, lang=args.lang)
    emit(response, args)
    return 0


def cmd_vidya(args):
    import KalaVidya
    if not args.direct:
        try:
            params = {"lang": args.lang}
            if getattr(args, "concept", None):
                params["concept"] = args.concept
            if getattr(args, "category", None):
                params["category"] = args.category
            if getattr(args, "search", None):
                params["q"] = args.search
            emit(json.loads(query_server(args.port, "/vidya", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")),
                  file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    lang = args.lang
    if getattr(args, "concept", None):
        entry = KalaVidya.get_concept(args.concept, lang)
        emit({"concept": entry, "found": entry is not None,
              "categories": KalaVidya.categories(lang)}, args)
    elif getattr(args, "search", None):
        results = KalaVidya.search_concepts(args.search, lang)
        emit({"search": results, "count": len(results), "query": args.search,
              "categories": KalaVidya.categories(lang)}, args)
    else:
        catalog = KalaVidya.concept_catalog(lang, category=getattr(args, "category", None))
        resp = {"catalog": catalog, "count": len(catalog),
                "categories": KalaVidya.categories(lang)}
        if getattr(args, "category", None):
            resp["category"] = args.category
        emit(resp, args)
    return 0


def cmd_kundali(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/kundali", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    emit(kd, args)
    return 0


def cmd_analysis(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/analysis", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    emit({"kundali": kd, "analysis": KalaChakra.generate_analysis(kd, lang=args.lang)}, args)
    return 0


def cmd_day_hora_muhurta(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    endpoint = "/hora" if args.command == "hora" else "/muhurta"
    func = KalaChakra.calculate_dina_horas if args.command == "hora" else KalaChakra.calculate_muhurtas
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, endpoint, params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    data = func(date_obj.year, date_obj.month, date_obj.day,
                args.tz, args.lat, args.lon, args.alt, lang=args.lang)
    emit(data, args)
    return 0


def cmd_ashtakoota(args):
    bride = {"year": args.bride_year, "month": args.bride_month, "day": args.bride_day,
             "hour": args.bride_hour, "minute": args.bride_minute, "tz": args.bride_tz}
    groom = {"year": args.groom_year, "month": args.groom_month, "day": args.groom_day,
             "hour": args.groom_hour, "minute": args.groom_minute, "tz": args.groom_tz}
    if not args.direct:
        try:
            payload = json.dumps({"bride": bride, "groom": groom,
                                  "ayanamsa": args.ayanamsa, "lang": args.lang}).encode()
            req = urllib.request.Request("http://127.0.0.1:{}/ashtakoota".format(args.port),
                                         data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read()
            emit(json.loads(text), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    result = KalaChakra.calculate_ashtakoota(bride, groom, ayanamsa=args.ayanamsa, lang=args.lang)
    emit(result, args)
    return 0


def cmd_gochara(args):
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if args.transit_date:
        t_obj = datetime.datetime.strptime(args.transit_date, DATE_FORMAT).date()
    else:
        t_obj = date_obj
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT),
                      "hour": str(args.hour), "minute": str(args.minute),
                      "transit_date": t_obj.strftime(DATE_FORMAT),
                      "transit_hour": str(args.transit_hour),
                      "transit_minute": str(args.transit_minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/gochara", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    gochara = KalaChakra.calculate_gochara(
        kd, t_obj.year, t_obj.month, t_obj.day, args.transit_hour, args.transit_minute,
        args.tz, args.lat, args.lon, lang=args.lang, ayanamsa=args.ayanamsa,
    )
    emit({"kundali": kd, "gochara": gochara}, args)
    return 0


def add_common(parser):
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="KalaSetu port (default 8642)")
    parser.add_argument("--direct", action="store_true", help="Compute directly instead of querying the daemon")
    parser.add_argument("--lat", type=float, default=23.1765)
    parser.add_argument("--lon", type=float, default=75.7885)
    parser.add_argument("--alt", type=float, default=0.0)
    parser.add_argument("--tz", type=float, default=5.5)
    parser.add_argument("--tithi-mode", default="traditional")
    parser.add_argument("--calendar-system", default="shaka")
    parser.add_argument("--month-system", default="amavasyanta")
    parser.add_argument("--festival-rule", default="vaishnava")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--dasha-depth", type=int, default=3, choices=[3, 4, 5],
                        help="Vimshottari tree depth: 3 MD/AD/PD, 4 +Sukshma, 5 +Prana")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", help="Write to file instead of stdout")


def build_parser():
    p = argparse.ArgumentParser(prog="kalayantra-cli", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common(p)

    common = argparse.ArgumentParser(add_help=False)
    add_common(common)

    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("day", parents=[common], help="Single day panchanga")
    d.add_argument("--date", required=True, help="DD-MM-YYYY")
    d.set_defaults(func=cmd_day)

    m = sub.add_parser("month", parents=[common], help="Whole month panchanga")
    m.add_argument("--year", type=int, default=datetime.date.today().year)
    m.add_argument("--month", type=int, default=datetime.date.today().month)
    m.set_defaults(func=cmd_month)

    r = sub.add_parser("range", parents=[common], help="Date range panchanga (up to 372 days)")
    r.add_argument("--start", required=True, help="DD-MM-YYYY")
    r.add_argument("--end", help="DD-MM-YYYY")
    r.add_argument("--days", type=int, default=1)
    r.set_defaults(func=cmd_range)

    f = sub.add_parser("festivals", parents=[common], help="Only days that have festivals in a range")
    f.add_argument("--start", required=True, help="DD-MM-YYYY")
    f.add_argument("--end", help="DD-MM-YYYY")
    f.add_argument("--days", type=int, default=365)
    f.set_defaults(func=cmd_festivals)

    c = sub.add_parser("search-city", parents=[common], help="Find a built-in/custom city")
    c.add_argument("--q", required=True)
    c.set_defaults(func=cmd_search_city)

    s = sub.add_parser("system-info", parents=[common], help="Runtime system information")
    s.set_defaults(func=cmd_system_info)

    k = sub.add_parser("kundali", parents=[common], help="Natal chart (D1/D3/D9 + vargas + dashas)")
    k.add_argument("--date", required=True, help="Birth date DD-MM-YYYY")
    k.add_argument("--hour", type=float, default=12.0, help="Birth hour (0-23)")
    k.add_argument("--minute", type=float, default=0.0, help="Birth minute")
    k.add_argument("--ayanamsa", default="lahiri",
                   help="lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce | sayana")
    k.set_defaults(func=cmd_kundali)

    an = sub.add_parser("analysis", parents=[common], help="Offline rule-based chart analysis")
    an.add_argument("--date", required=True, help="Birth date DD-MM-YYYY")
    an.add_argument("--hour", type=float, default=12.0)
    an.add_argument("--minute", type=float, default=0.0)
    an.add_argument("--ayanamsa", default="lahiri")
    an.set_defaults(func=cmd_analysis)

    bo = sub.add_parser("bodha", parents=[common],
                        help="Structured Jyotisa reasoning (KalaBodha)")
    bo.add_argument("--date", required=True, help="Birth date DD-MM-YYYY")
    bo.add_argument("--hour", type=float, default=12.0)
    bo.add_argument("--minute", type=float, default=0.0)
    bo.add_argument("--ayanamsa", default="lahiri")
    bo.add_argument("--sensitivity", action="store_true",
                    help="Include the birth-time sensitivity report")
    bo.set_defaults(func=cmd_bodha)

    me = sub.add_parser("medha", parents=[common],
                        help="Offline AI reading (KalaMedha) over the evidence graph")
    me.add_argument("--date", required=True, help="Birth date DD-MM-YYYY")
    me.add_argument("--hour", type=float, default=12.0)
    me.add_argument("--minute", type=float, default=0.0)
    me.add_argument("--ayanamsa", default="lahiri")
    me.add_argument("--question", help="Optional natural-language question about the chart")
    me.add_argument("--llm", action="store_true",
                    help="Try the optional local LLM hook (falls back to rules)")
    me.set_defaults(func=cmd_medha)

    vd = sub.add_parser("vidya", parents=[common],
                        help="KalaVidya informational layer — concepts, formulas and examples")
    vd.add_argument("concept", nargs="?", help="Concept id or title to fetch in full (e.g. tithi)")
    vd.add_argument("--category", help="Filter the catalog by category slug (e.g. panchanga)")
    vd.add_argument("--search", help="Keyword search across titles/summaries")
    vd.set_defaults(func=cmd_vidya)

    gc = sub.add_parser("gochara", parents=[common],
                        help="Gochara — planetary transits against a natal chart")
    gc.add_argument("--date", required=True, help="Birth date DD-MM-YYYY")
    gc.add_argument("--hour", type=float, default=12.0, help="Birth hour (0-23)")
    gc.add_argument("--minute", type=float, default=0.0, help="Birth minute")
    gc.add_argument("--transit-date", help="Transit moment DD-MM-YYYY (defaults to birth date)")
    gc.add_argument("--transit-hour", type=float, default=12.0, help="Transit hour (0-23)")
    gc.add_argument("--transit-minute", type=float, default=0.0, help="Transit minute")
    gc.add_argument("--ayanamsa", default="lahiri",
                    help="lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce | sayana")
    gc.set_defaults(func=cmd_gochara)

    ho = sub.add_parser("hora", parents=[common], help="24 Chaldean dina horas of a day")
    ho.add_argument("--date", required=True, help="DD-MM-YYYY")
    ho.set_defaults(func=cmd_day_hora_muhurta, command="hora")

    mu = sub.add_parser("muhurta", parents=[common], help="30 day/night muhurtas of a day")
    mu.add_argument("--date", required=True, help="DD-MM-YYYY")
    mu.set_defaults(func=cmd_day_hora_muhurta, command="muhurta")

    ak = sub.add_parser("ashtakoota", parents=[common], help="Ashtakoota (Guna Milan) compatibility")
    ak.add_argument("--bride-year", type=int, required=True)
    ak.add_argument("--bride-month", type=int, required=True)
    ak.add_argument("--bride-day", type=int, required=True)
    ak.add_argument("--bride-hour", type=int, default=12, help="Bride birth hour (0-23)")
    ak.add_argument("--bride-minute", type=int, default=0)
    ak.add_argument("--bride-tz", type=float, default=5.5)
    ak.add_argument("--groom-year", type=int, required=True)
    ak.add_argument("--groom-month", type=int, required=True)
    ak.add_argument("--groom-day", type=int, required=True)
    ak.add_argument("--groom-hour", type=int, default=12)
    ak.add_argument("--groom-minute", type=int, default=0)
    ak.add_argument("--groom-tz", type=float, default=5.5)
    ak.add_argument("--ayanamsa", default="lahiri")
    ak.set_defaults(func=cmd_ashtakoota)

    return p


def main():
    args = build_parser().parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()