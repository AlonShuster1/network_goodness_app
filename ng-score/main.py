import json
import os
from contextlib import asynccontextmanager

import geopandas as gpd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tqdm import tqdm

from src.models.city import City
from src.models.points import Points
from src.services.demand_calculator import get_demand_points_from_neighborhood
from src.api.routes import router

_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "beer_sheva.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    with open(_DATA_FILE) as f:
        data = json.load(f)

    city = City(
        name=data["name"],
        area=data["area"],
        hood_borders=data["hood_borders"],
        hood_population=data["hood_population"],
        area_for_each_neighborhood=data["area_for_each_neighborhood"],
    )

    points = Points()
    print("Building demand points (first run downloads from OSM, subsequent runs use cache)...")

    for i in tqdm(range(len(city.hood_borders))):
        df = get_demand_points_from_neighborhood(
            city.hood_borders[i], city.hood_population[i], i
        )
        points_latlon = gpd.GeoSeries(df["point"], crs="EPSG:2039").to_crs(epsg=4326)
        points.add_area_in_demand_zone(i + 1, city.area_for_each_neighborhood[i])

        for idx, point_geom in points_latlon.items():
            lon = point_geom.x
            lat = point_geom.y
            demand = df.loc[idx, "estimated_people"]
            points.add_demand_point(i + 1, lat, lon, demand)

    app.state.points = points
    app.state.city = city
    print("Startup complete. Server ready at http://localhost:8000")
    yield


app = FastAPI(title="Network Goodness Score", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
