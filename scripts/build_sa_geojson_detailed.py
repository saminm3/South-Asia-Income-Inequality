# scripts/build_sa_geojson_detailed.py
import os, io, hashlib, requests, geopandas as gpd

BASE = os.path.dirname(os.path.dirname(__file__))
P = lambda *xs: os.path.join(BASE, *xs)

# SAARC ISO-3 codes
SA_ISOS = ["AFG", "BGD", "BTN", "IND", "MDV", "NPL", "PAK", "LKA"]

# Natural Earth 1:50m countries (detailed) GeoJSON (official mirror)
WORLD_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
    "ne_50m_admin_0_countries.geojson"
)

def download_world_geojson(dest_path: str) -> bytes:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    r = requests.get(WORLD_GEOJSON_URL, timeout=120)
    r.raise_for_status()
    data = r.content
    with open(dest_path, "wb") as f:
        f.write(data)
    return data

def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def main():
    cache_world = P("data", "geo", "world_50m.geojson")
    out_path    = P("data", "geo", "sa_countries.geojson")

    # Download (or re-use cached) world file
    if not os.path.exists(cache_world):
        print("⬇️  Downloading Natural Earth 1:50m countries (GeoJSON)…")
        data = download_world_geojson(cache_world)
        print("✅ Downloaded. MD5:", md5(data))
    else:
        print("📦 Using cached:", cache_world)

    # Read with GeoPandas
    world = gpd.read_file(cache_world)

    # Normalize field names (case-insensitive search)
    cols_lower = {c.lower(): c for c in world.columns}
    name_col = cols_lower.get("name") or cols_lower.get("admin") or "NAME"
    iso3_col = cols_lower.get("iso_a3") or cols_lower.get("adm0_a3") or "ISO_A3"

    # Keep only the columns we need
    gdf = world[[name_col, iso3_col, "geometry"]].copy()
    gdf = gdf.rename(columns={name_col: "ADMIN", iso3_col: "ISO_A3"})

    # Filter to SAARC
    gdf = gdf[gdf["ISO_A3"].isin(SA_ISOS)].copy()

    # Ensure WGS84 (lon/lat)
    gdf = gdf.to_crs(4326)

    # Write final detailed file
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"✅ Wrote {out_path} with {len(gdf)} countries:", ", ".join(gdf["ADMIN"]))

if __name__ == "__main__":
    main()
