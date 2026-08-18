"""Lớp nền OpenStreetMap quanh vùng trồng: sử dụng đất, đường, thuỷ hệ, nhà.

Dùng để có bối cảnh vector cho bản đồ và để đối chiếu ranh giới thửa.
Nguồn: Overpass API (miễn phí). Kết quả xuất GeoJSON + GeoPackage nhiều lớp.
"""
import os

import geopandas as gpd
import requests
from shapely.geometry import LineString, Polygon

BASE = os.path.expanduser("~/Documents/GIS_RiTi_TrangAn")
OVERPASS = "https://overpass-api.de/api/interpreter"
PAD_DEG = 0.006  # ~650 m, đủ rộng để có bối cảnh làng xóm


def main():
    aoi = gpd.read_file(f"{BASE}/data/out/aoi_riti.geojson")
    minx, miny, maxx, maxy = aoi.total_bounds
    s, w = miny - PAD_DEG, minx - PAD_DEG
    n, e = maxy + PAD_DEG, maxx + PAD_DEG
    bbox = f"{s},{w},{n},{e}"

    q = f"""
    [out:json][timeout:120];
    (
      way["landuse"]({bbox});
      way["natural"]({bbox});
      way["waterway"]({bbox});
      way["highway"]({bbox});
      way["building"]({bbox});
      way["place"]({bbox});
      relation["landuse"]({bbox});
    );
    out geom;
    """
    r = requests.post(OVERPASS, data={"data": q}, timeout=180,
                      headers={"User-Agent": "GIS survey RiTi farm (educational)"})
    r.raise_for_status()
    els = r.json()["elements"]
    print(f"Overpass trả về {len(els)} đối tượng")

    feats = []
    for el in els:
        geom = el.get("geometry")
        if not geom or len(geom) < 2:
            continue
        pts = [(p["lon"], p["lat"]) for p in geom]
        tags = el.get("tags", {})
        closed = pts[0] == pts[-1] and len(pts) >= 4
        # Đường/thuỷ hệ luôn là line kể cả khi khép kín (vòng xuyến, mương vòng)
        as_area = closed and not (tags.get("highway") or tags.get("waterway"))
        try:
            g = Polygon(pts) if as_area else LineString(pts)
        except Exception:
            continue
        if not g.is_valid:
            g = g.buffer(0)
        if g.is_empty:
            continue
        feats.append({
            "geometry": g,
            "osm_id": el["id"],
            "kind": ("landuse" if "landuse" in tags else
                     "building" if "building" in tags else
                     "waterway" if "waterway" in tags else
                     "highway" if "highway" in tags else
                     "natural" if "natural" in tags else "other"),
            "value": (tags.get("landuse") or tags.get("building") or
                      tags.get("waterway") or tags.get("highway") or
                      tags.get("natural") or ""),
            "name": tags.get("name", ""),
        })

    gdf = gpd.GeoDataFrame(feats, crs="EPSG:4326")
    print(gdf.groupby(["kind", "value"]).size().sort_values(ascending=False).head(20))

    gpkg = f"{BASE}/data/out/osm_context.gpkg"
    for kind, sub in gdf.groupby("kind"):
        sub.to_file(gpkg, driver="GPKG", layer=kind)
        sub.to_file(f"{BASE}/data/out/osm_{kind}.geojson", driver="GeoJSON")

    # Thửa đất nông nghiệp giao với vùng trồng
    land = gdf[gdf["kind"] == "landuse"]
    if len(land):
        hit = gpd.overlay(land.to_crs("EPSG:32648"),
                          aoi.to_crs("EPSG:32648")[["geometry"]], how="intersection")
        if len(hit):
            hit["area_ha"] = hit.area / 10_000
            print("\nthửa OSM chồng lấn vùng trồng:")
            print(hit[["value", "name", "area_ha"]].sort_values("area_ha", ascending=False))
            hit.to_crs("EPSG:4326").to_file(
                f"{BASE}/data/out/osm_parcels_in_aoi.geojson", driver="GeoJSON")
        else:
            print("\nOSM chưa có thửa đất nào được vẽ bên trong vùng trồng này.")
    print("\nđã ghi:", gpkg)


if __name__ == "__main__":
    main()
