import json
import os
from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.models.network import Network

router = APIRouter()

_DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "beer_sheva.json"
)


class NodeList(BaseModel):
    nodes: List[List[float]]


def _safe_call(fn):
    try:
        return fn()
    except ZeroDivisionError:
        return 0.0


@router.post("/calculate")
async def calculate(body: NodeList, request: Request):
    if len(body.nodes) < 2:
        return {"K": 0, "L": 0.0, "network_inertia": 0.0,
                "formula3": 0.0, "formula4": 0.0, "formula5": 0.0, "formula6": 0.0}

    points = request.app.state.points
    city = request.app.state.city

    net = Network(city=city)
    for node in body.nodes:
        net.add_node(tuple(node))

    net.calculate_network(points)

    return {
        "K": net.K,
        "L": net.L,
        "network_inertia": net.network_inertia,
        "formula3": _safe_call(net.formula3),
        "formula4": _safe_call(net.formula4),
        "formula5": _safe_call(net.formula5),
        "formula6": _safe_call(net.formula6),
    }


@router.get("/neighborhoods")
async def neighborhoods():
    with open(_DATA_FILE) as f:
        data = json.load(f)
    return {"neighborhoods": data["hood_borders"]}
