import os

import geopandas as gpd
import osmnx as ox
from shapely.geometry import Polygon as ShapelyPolygon

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(_SRC_DIR)
CACHE_DIR = os.path.join(PROJECT_ROOT, "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_demand_points_from_neighborhood(hood_border, hood_population, hood_id):
    file_name = os.path.join(CACHE_DIR, f"buildings_{hood_id}.geojson")

    if os.path.exists(file_name):
        print(f"  [Cache] Loading hood {hood_id} from local cache...")
        buildings = gpd.read_file(file_name)
    else:
        print(f"  [Cache] Fetching hood {hood_id} from OSM and saving to cache...")
        pts_lonlat = [(lon, lat) for (lat, lon) in hood_border]
        poly = ShapelyPolygon(pts_lonlat)
        buildings = ox.features_from_polygon(poly, tags={"building": True})
        buildings.to_file(file_name, driver="GeoJSON")
        print(f"  [Cache] Saved -> {file_name}")

    buildings = buildings.to_crs(epsg=2039)
    buildings["area_m2"] = buildings.area
    buildings["point"] = buildings.geometry.representative_point()
    total_area = buildings["area_m2"].sum()
    buildings["estimated_people"] = (buildings["area_m2"] / total_area) * hood_population
    return buildings


def compute_neighborhood_areas(hood_borders):
    area_for_each_neighborhood = []

    for hood_border in hood_borders:
        pts_lonlat = [(lon, lat) for (lat, lon) in hood_border]
        poly = ShapelyPolygon(pts_lonlat)
        hood_poly = gpd.GeoSeries([poly], crs="EPSG:4326").to_crs(epsg=2039)
        area_for_each_neighborhood.append(hood_poly.area.iloc[0] / 1000000)

    return area_for_each_neighborhood
