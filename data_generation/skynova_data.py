"""
Shared master data for the fictional airline SkyNova.
Every PDF is generated from this module so that routes, distances, fares,
aircraft and performance figures are consistent across all documents.

DISCLAIMER: SkyNova Airlines is a fictional company created for an
educational challenge. Any resemblance to real airlines is coincidental.
"""
import random

AIRLINE = "SkyNova Airlines"
IATA = "NV"
HUB = "Madrid-Barajas (MAD)"
HQ_ADDRESS = "SkyNova Airlines S.A., Avenida de la Hispanidad 42, 28042 Madrid, Spain"

# ---------------------------------------------------------------- Fleet
FLEET = [
    # model, count, seats total, business, premium eco, economy, pitch eco, wifi, power, ife, avg age
    dict(model="ATR 72-600", brand="SkyNova Connect", count=6, seats=70, business=0, premium=0, economy=70,
         pitch='30"', wifi="No", power="USB-A at every seat", ife="None (stream not available)", age=6.1, haul="Regional"),
    dict(model="Airbus A320neo", brand="SkyNova", count=18, seats=180, business=12, premium=0, economy=168,
         pitch='30"', wifi="Yes", power="USB-C at every seat", ife="SkyNova Stream (own device)", age=4.3, haul="Short/medium-haul"),
    dict(model="Airbus A321neo", brand="SkyNova", count=10, seats=210, business=16, premium=0, economy=194,
         pitch='30"', wifi="Yes", power="USB-C at every seat", ife="SkyNova Stream (own device)", age=3.2, haul="Short/medium-haul"),
    dict(model="Airbus A321XLR", brand="SkyNova", count=4, seats=190, business=20, premium=0, economy=170,
         pitch='31"', wifi="Yes", power="USB-C + AC power at every seat", ife='13" seatback screens (Business), 10" (Economy)', age=1.1, haul="Long-haul (thin routes)"),
    dict(model="Airbus A350-900", brand="SkyNova", count=6, seats=315, business=32, premium=24, economy=259,
         pitch='31"', wifi="Yes", power="USB-C + AC power at every seat", ife='17" (Business), 13" (Premium), 11" (Economy)', age=5.4, haul="Long-haul"),
]
SEATS = {f["model"]: f["seats"] for f in FLEET}

# ---------------------------------------------------------------- Routes
# code, city, country, distance_km (great circle from origin), aircraft, weekly frequency, haul, origin
ROUTES = [
    # Domestic
    dict(origin="MAD", dest="BIO", city="Bilbao", country="Spain", km=318, ac="ATR 72-600", freq=21, haul="Domestic"),
    dict(origin="MAD", dest="SCQ", city="Santiago de Compostela", country="Spain", km=488, ac="ATR 72-600", freq=14, haul="Domestic"),
    dict(origin="MAD", dest="AGP", city="Malaga", country="Spain", km=430, ac="Airbus A320neo", freq=21, haul="Domestic"),
    dict(origin="MAD", dest="PMI", city="Palma de Mallorca", country="Spain", km=547, ac="Airbus A320neo", freq=28, haul="Domestic"),
    dict(origin="MAD", dest="TFN", city="Tenerife North", country="Spain", km=1760, ac="Airbus A321neo", freq=14, haul="Domestic"),
    dict(origin="MAD", dest="BCN", city="Barcelona", country="Spain", km=483, ac="Airbus A321neo", freq=35, haul="Domestic"),
    # Europe from MAD
    dict(origin="MAD", dest="LIS", city="Lisbon", country="Portugal", km=512, ac="Airbus A320neo", freq=21, haul="Europe"),
    dict(origin="MAD", dest="CDG", city="Paris Charles de Gaulle", country="France", km=1064, ac="Airbus A321neo", freq=28, haul="Europe"),
    dict(origin="MAD", dest="LHR", city="London Heathrow", country="United Kingdom", km=1246, ac="Airbus A321neo", freq=28, haul="Europe"),
    dict(origin="MAD", dest="FCO", city="Rome Fiumicino", country="Italy", km=1365, ac="Airbus A320neo", freq=21, haul="Europe"),
    dict(origin="MAD", dest="FRA", city="Frankfurt", country="Germany", km=1420, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="MAD", dest="AMS", city="Amsterdam", country="Netherlands", km=1480, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="MAD", dest="MUC", city="Munich", country="Germany", km=1493, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="MAD", dest="CPH", city="Copenhagen", country="Denmark", km=2070, ac="Airbus A320neo", freq=7, haul="Europe"),
    dict(origin="MAD", dest="ATH", city="Athens", country="Greece", km=2370, ac="Airbus A321neo", freq=7, haul="Europe"),
    # Europe from BCN
    dict(origin="BCN", dest="CDG", city="Paris Charles de Gaulle", country="France", km=830, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="BCN", dest="FCO", city="Rome Fiumicino", country="Italy", km=860, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="BCN", dest="LHR", city="London Heathrow", country="United Kingdom", km=1146, ac="Airbus A320neo", freq=14, haul="Europe"),
    dict(origin="BCN", dest="AMS", city="Amsterdam", country="Netherlands", km=1240, ac="Airbus A320neo", freq=7, haul="Europe"),
    # Long-haul
    dict(origin="MAD", dest="BOS", city="Boston", country="United States", km=5450, ac="Airbus A321XLR", freq=5, haul="Long-haul"),
    dict(origin="MAD", dest="YUL", city="Montreal", country="Canada", km=5520, ac="Airbus A321XLR", freq=4, haul="Long-haul"),
    dict(origin="MAD", dest="JFK", city="New York JFK", country="United States", km=5770, ac="Airbus A350-900", freq=7, haul="Long-haul"),
    dict(origin="MAD", dest="MIA", city="Miami", country="United States", km=7110, ac="Airbus A350-900", freq=5, haul="Long-haul"),
    dict(origin="MAD", dest="BOG", city="Bogota", country="Colombia", km=8030, ac="Airbus A350-900", freq=4, haul="Long-haul"),
    dict(origin="MAD", dest="MEX", city="Mexico City", country="Mexico", km=9070, ac="Airbus A350-900", freq=5, haul="Long-haul"),
    dict(origin="MAD", dest="EZE", city="Buenos Aires", country="Argentina", km=10040, ac="Airbus A350-900", freq=3, haul="Long-haul"),
]

# Flight numbers & schedule (outbound departure local time, days of operation)
_DAYS_BY_FREQ = {
    3: "Mon, Wed, Fri", 4: "Mon, Wed, Fri, Sun", 5: "Mon, Tue, Thu, Fri, Sun",
    7: "Daily", 14: "Daily (2x)", 21: "Daily (3x)", 28: "Daily (4x)", 35: "Daily (5x)",
}
_DEP_TIMES = {
    "BIO": "07:10 / 13:40 / 19:55", "SCQ": "08:05 / 18:30", "AGP": "07:30 / 12:15 / 20:10",
    "PMI": "06:50 / 10:25 / 15:40 / 20:30", "TFN": "09:15 / 17:45", "BCN": "06:30 / 09:00 / 13:00 / 17:00 / 21:00",
    "LIS": "07:20 / 13:05 / 19:40", "CDG": "07:00 / 11:30 / 15:50 / 20:05", "LHR": "07:45 / 11:10 / 16:20 / 19:50",
    "FCO": "08:10 / 13:35 / 19:15", "FRA": "07:35 / 18:10", "AMS": "08:20 / 17:55", "MUC": "07:55 / 18:40",
    "CPH": "10:30", "ATH": "11:15",
    "BCN-CDG": "07:40 / 18:20", "BCN-FCO": "09:05 / 19:30", "BCN-LHR": "08:15 / 17:40", "BCN-AMS": "10:20",
    "BOS": "12:05", "YUL": "12:40", "JFK": "11:55", "MIA": "13:10", "BOG": "15:45", "MEX": "14:20", "EZE": "23:55",
}


_BASE = {"Domestic": 300, "MAD-Europe": 100, "BCN-Europe": 700, "Long-haul": 600}
_COUNTER = {k: 0 for k in _BASE}


def flight_number(r):
    group = r["haul"] if r["haul"] != "Europe" else f'{r["origin"]}-Europe'
    n = _BASE[group] + _COUNTER[group] * 10
    _COUNTER[group] += 1
    return f"{IATA}{n}"


for _r in ROUTES:
    _r["route"] = f'{_r["origin"]}-{_r["dest"]}'
    _r["flight"] = flight_number(_r)
    key = _r["dest"] if _r["origin"] == "MAD" else _r["route"]
    _r["dep_times"] = _DEP_TIMES[key]
    _r["days"] = _DAYS_BY_FREQ[_r["freq"]]
    _r["block"] = None

# Approximate block times (h:mm)
for _r in ROUTES:
    km = _r["km"]
    minutes = int(35 + km / 780 * 60) if _r["ac"] != "ATR 72-600" else int(30 + km / 480 * 60)
    _r["block"] = f"{minutes // 60}h {minutes % 60:02d}m"


def eu261_band(km):
    """Compensation band per EC 261/2004 (all SkyNova flights depart or arrive in the EU on an EU carrier)."""
    if km <= 1500:
        return 250
    if km <= 3500:
        return 400
    return 600


# ---------------------------------------------------------------- Performance data (Q3 2026 + Q3 2025)
MONTHS = [("Jul 2026", 31), ("Aug 2026", 31), ("Sep 2026", 30)]
MONTH_ADJ = {"Jul 2026": -2.5, "Aug 2026": -7.5, "Sep 2026": +2.0}  # Aug: ATC strikes in France + heat waves
BASE_OTP = {
    "BIO": 88, "SCQ": 84, "AGP": 86, "PMI": 79, "TFN": 83, "BCN": 85, "LIS": 87, "CDG": 76, "LHR": 78,
    "FCO": 80, "FRA": 84, "AMS": 81, "MUC": 85, "CPH": 86, "ATH": 82,
    "BCN-CDG": 74, "BCN-FCO": 79, "BCN-LHR": 77, "BCN-AMS": 80,
    "BOS": 83, "YUL": 81, "JFK": 79, "MIA": 77, "BOG": 74, "MEX": 72, "EZE": 78,
}
BASE_LF = {"Domestic": 84, "Europe": 86, "Long-haul": 88}
DELAY_CAUSES = ["Air traffic control (ATC)", "Weather", "Late inbound aircraft (reactionary)",
                "Technical / maintenance", "Ground handling & turnaround", "Crew", "Airport infrastructure", "Security & other"]
CAUSE_SHARE = {
    "Jul 2026": [22, 9, 31, 11, 13, 5, 6, 3],
    "Aug 2026": [34, 12, 27, 8, 9, 4, 4, 2],
    "Sep 2026": [17, 8, 33, 14, 14, 6, 5, 3],
}


def _key(r):
    return r["dest"] if r["origin"] == "MAD" else r["route"]


def generate_performance(seed=2026, year_shift=0.0, months=MONTHS, adj=MONTH_ADJ):
    rng = random.Random(seed)
    rows = []
    for mname, days in months:
        for r in ROUTES:
            sched = round(r["freq"] * days / 7) * 2  # both directions
            cancel_rate = {"Jul 2026": 0.008, "Aug 2026": 0.019, "Sep 2026": 0.006}.get(mname, 0.01)
            if r["haul"] == "Long-haul":
                cancel_rate *= 0.4
            cancelled = max(0, int(round(sched * cancel_rate * rng.uniform(0.5, 1.6))))
            if r["origin"] == "BCN" or r["dest"] == "CDG":
                cancelled += 1 if mname.startswith("Aug") else 0
            operated = sched - cancelled
            otp = BASE_OTP[_key(r)] + adj.get(mname, 0) + rng.uniform(-2.5, 2.5) + year_shift
            if r["dest"] == "CDG" and mname.startswith("Aug"):
                otp -= 6  # French ATC strikes 6-8 and 21-22 August
            otp = max(55.0, min(96.0, otp))
            on_time = int(round(operated * otp / 100))
            otp = round(on_time / operated * 100, 1)
            avg_delay = round(rng.uniform(32, 48) + (100 - otp) * 0.6 + (12 if r["haul"] == "Long-haul" else 0), 0)
            lf = BASE_LF[r["haul"]] + {"Jul 2026": 4, "Aug 2026": 6, "Sep 2026": 0}.get(mname, 2) + rng.uniform(-3, 3)
            if r["haul"] == "Domestic" and r["dest"] in ("PMI", "TFN", "AGP") and not mname.startswith("Sep"):
                lf += 3
            lf = round(min(97.5, lf), 1)
            pax = int(operated * SEATS[r["ac"]] * lf / 100)
            bags = int(round(pax / 1000 * rng.uniform(3.0, 6.5) * (1.4 if r["haul"] == "Long-haul" else 1.0)))
            complaints = int(round(pax / 10000 * (18 + (100 - otp) * 1.1 + rng.uniform(-4, 4))))
            nps = int(round(48 - (100 - otp) * 0.55 + rng.uniform(-5, 5) + (6 if r["haul"] == "Long-haul" else 0)))
            rows.append(dict(
                month=mname, route=r["route"], flight=r["flight"], destination=r["city"], haul=r["haul"],
                aircraft=r["ac"], distance_km=r["km"], scheduled_flights=sched, operated_flights=operated,
                cancelled_flights=cancelled, on_time_flights=on_time, otp_pct=otp,
                avg_delay_min=int(avg_delay), passengers=pax, load_factor_pct=lf,
                mishandled_bags=bags, complaints=complaints, nps=nps,
            ))
    return rows


PERF_2026 = generate_performance()
PERF_2025 = generate_performance(
    seed=2025, year_shift=-1.8,
    months=[("Jul 2025", 31), ("Aug 2025", 31), ("Sep 2025", 30)],
    adj={"Jul 2025": -2.0, "Aug 2025": -4.0, "Sep 2025": +1.0},
)


def network_summary(rows, month=None):
    sel = [x for x in rows if month is None or x["month"] == month]
    sched = sum(x["scheduled_flights"] for x in sel)
    oper = sum(x["operated_flights"] for x in sel)
    canc = sum(x["cancelled_flights"] for x in sel)
    ontime = sum(x["on_time_flights"] for x in sel)
    pax = sum(x["passengers"] for x in sel)
    seats = sum(x["operated_flights"] * SEATS[x["aircraft"]] for x in sel)
    bags = sum(x["mishandled_bags"] for x in sel)
    compl = sum(x["complaints"] for x in sel)
    nps = sum(x["nps"] * x["passengers"] for x in sel) / pax
    return dict(scheduled=sched, operated=oper, cancelled=canc, on_time=ontime,
                otp=round(ontime / oper * 100, 1), cancel_rate=round(canc / sched * 100, 2),
                pax=pax, lf=round(pax / seats * 100, 1), bags_per_1000=round(bags / pax * 1000, 2),
                complaints_per_10k=round(compl / pax * 10000, 2), complaints=compl, bags=bags, nps=round(nps, 0))
