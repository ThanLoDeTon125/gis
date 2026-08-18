"""Khí hậu theo ngày tại RiTi Organic Farm, 12 THÁNG (Open-Meteo, miễn phí).

Hai đầu API khác nhau, phải ghép:

  * archive-api (ERA5 tái phân tích) trả về nhiều năm nhưng TRỄ ~5 ngày.
  * api.open-meteo.com (mô hình dự báo) chỉ lùi được ~92 ngày.

Lấy phần dài từ archive, vá mấy ngày cuối bằng forecast. Tên biến độ ẩm đất ở
hai đầu KHÁC NHAU (ERA5 chia tầng 0-7/7-28 cm, mô hình dự báo chia 0-1/1-3 cm)
nên phải khai báo riêng, không dùng chung danh sách.

Khí hậu là dữ liệu ĐIỂM cho cả farm: 9 ha thì mưa và nhiệt độ không khác nhau
giữa các lô. Phần khác nhau theo lô nằm ở ảnh vệ tinh, không nằm ở đây.
"""
import csv
import os
from datetime import date, timedelta

import requests

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
LAT, LON = 20.2579952, 105.854332

END = date(2026, 8, 12)
START = date(2025, 8, 12)

DAILY = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "relative_humidity_2m_mean", "precipitation_sum", "rain_sum",
    "precipitation_hours", "et0_fao_evapotranspiration",
    "shortwave_radiation_sum", "wind_speed_10m_max",
]
SOIL_ARCHIVE = ["soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm",
                "soil_moisture_28_to_100cm", "soil_temperature_0_to_7cm"]
SOIL_FORECAST = ["soil_moisture_0_to_1cm", "soil_moisture_3_to_9cm",
                 "soil_moisture_27_to_81cm", "soil_temperature_0cm"]
SOIL_OUT = ["sm_nong", "sm_giua", "sm_sau", "nhiet_dat"]


def get(url, soil, start, end):
    r = requests.get(url, timeout=90, params={
        "latitude": LAT, "longitude": LON,
        "start_date": start.isoformat(), "end_date": end.isoformat(),
        "daily": ",".join(DAILY), "hourly": ",".join(soil),
        "timezone": "Asia/Bangkok"})
    r.raise_for_status()
    return r.json()


def daily_soil(js, soil):
    hourly = js.get("hourly") or {}
    agg = {}
    for i, t in enumerate(hourly.get("time", [])):
        day = t[:10]
        agg.setdefault(day, [[] for _ in soil])
        for k, name in enumerate(soil):
            v = (hourly.get(name) or [None] * (i + 1))[i]
            if v is not None:
                agg[day][k].append(v)
    return {d: [round(sum(v) / len(v), 4) if v else "" for v in cols]
            for d, cols in agg.items()}


def main():
    rows, soil_rows = {}, {}
    a = get("https://archive-api.open-meteo.com/v1/archive", SOIL_ARCHIVE,
            START, END)
    for i, t in enumerate(a["daily"]["time"]):
        vals = [a["daily"][k][i] for k in DAILY]
        if vals[4] is not None:
            rows[t] = vals
    soil_rows.update(daily_soil(a, SOIL_ARCHIVE))
    print(f"archive ERA5 : {len(rows)} ngày có số liệu")

    missing = [(START + timedelta(days=i)).isoformat()
               for i in range((END - START).days + 1)]
    missing = [d for d in missing if d not in rows]
    if missing:
        lo = max(date.fromisoformat(missing[0]), END - timedelta(days=90))
        f = get("https://api.open-meteo.com/v1/forecast", SOIL_FORECAST, lo, END)
        n = 0
        for i, t in enumerate(f["daily"]["time"]):
            if t in rows:
                continue
            vals = [f["daily"][k][i] for k in DAILY]
            if vals[4] is not None:
                rows[t] = vals
                n += 1
        for d, v in daily_soil(f, SOIL_FORECAST).items():
            soil_rows.setdefault(d, v)
        print(f"vá bằng forecast: thêm {n} ngày ({len(missing)} ngày còn thiếu "
              f"trước khi vá)")

    days = sorted(rows)
    with open(f"{BASE}/data/out/climate_daily.csv", "w", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["date"] + DAILY)
        w.writerows([[d] + rows[d] for d in days])
    with open(f"{BASE}/data/out/soil_moisture_daily.csv", "w", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["date"] + SOIL_OUT)
        for d in sorted(soil_rows):
            w.writerow([d] + soil_rows[d])

    ix = {k: i for i, k in enumerate(DAILY)}
    rain = [rows[d][ix["precipitation_sum"]] or 0 for d in days]
    et0 = [rows[d][ix["et0_fao_evapotranspiration"]] or 0 for d in days]
    tmax = [rows[d][ix["temperature_2m_max"]] for d in days if rows[d][ix["temperature_2m_max"]]]
    tmin = [rows[d][ix["temperature_2m_min"]] for d in days if rows[d][ix["temperature_2m_min"]]]
    by_month = {}
    for d, r in ((d, rows[d]) for d in days):
        by_month.setdefault(d[:7], [0, 0])
        by_month[d[:7]][0] += r[ix["precipitation_sum"]] or 0
        by_month[d[:7]][1] += 1
    print(f"\nkỳ dữ liệu   : {days[0]} -> {days[-1]} ({len(days)} ngày)")
    print(f"tổng mưa     : {sum(rain):,.0f} mm | ET0 {sum(et0):,.0f} mm "
          f"-> cân bằng nước {sum(rain)-sum(et0):+,.0f} mm")
    print(f"nhiệt độ     : {min(tmin):.1f}–{max(tmax):.1f} °C")
    print("mưa theo tháng:", "  ".join(f"{m}={v[0]:.0f}" for m, v in sorted(by_month.items())))
    print("đã ghi: climate_daily.csv, soil_moisture_daily.csv")


if __name__ == "__main__":
    main()
