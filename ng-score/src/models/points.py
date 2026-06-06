from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DemandPoint:
    demand_zone: int
    x: float
    y: float
    q: float


class Points:
    def __init__(self):
        self._demand_points = []
        self._demand_zone_centers = defaultdict(float)
        self._q_in_demand_zone = defaultdict(float)
        self._area_in_demand_zone = defaultdict(float)
        self.__centers_dirty = False

    def __repr__(self) -> str:
        return (f"Points(demand_points={len(self._demand_points)}, "
                f"zones={len(self._demand_zone_centers)})")

    def add_demand_point(self, demand_zone: int, x: float, y: float, q: float) -> None:
        if None in (demand_zone, x, y, q):
            raise ValueError(f"Missing values. Received: zone={demand_zone}, x={x}, y={y}, q={q}")

        self._demand_points.append(DemandPoint(demand_zone, x, y, q))
        self.__centers_dirty = True

    def add_area_in_demand_zone(self, zone: int, area: int) -> None:
        self._area_in_demand_zone[zone] = area

    @property
    def demand_zone_centers(self):
        if self.__centers_dirty:
            self.__calculate_zone_demand_centers()
            self.__centers_dirty = False
        return self._demand_zone_centers

    @property
    def q_in_demand_zone(self):
        return self._q_in_demand_zone

    @property
    def area_in_demand_zone(self):
        return self._area_in_demand_zone

    def __calculate_zone_demand_centers(self):
        q_x_nominator = defaultdict(float)
        q_y_nominator = defaultdict(float)

        self._q_in_demand_zone.clear()
        self._demand_zone_centers.clear()

        for p in self._demand_points:
            q_x_nominator[p.demand_zone] += p.x * p.q
            q_y_nominator[p.demand_zone] += p.y * p.q
            self._q_in_demand_zone[p.demand_zone] += p.q

        for zone, total_q in self._q_in_demand_zone.items():
            if total_q == 0:
                continue  # Prevent ZeroDivisionError if a zone has exactly 0 population.

            center_x = q_x_nominator[zone] / total_q
            center_y = q_y_nominator[zone] / total_q
            self._demand_zone_centers[zone] = (center_x, center_y)
