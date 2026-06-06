from pyproj import Transformer
from shapely.geometry import Point, LineString

from .city import City
from .points import Points


class Network:
    def __init__(self, city: City, gravitating: float = 0.8, attracting: float = 0.4):
        self.city = city
        self._gravitating = gravitating
        self._attracting = attracting
        self._L = 0
        self._K = 0
        self._network_inertia = 0
        self._all_of_demand_zones_q = 0
        self._gravitating_demand_zones_area = 0
        self.geo_route = None
        self._network_nodes = []
        self.__network_dirty = False
        self.transformer = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)

    def __repr__(self) -> str:
        return (f"Network(nodes={len(self._network_nodes)}, "
                f"L={self._L:.2f}km, K={self._K})")

    def add_node(self, node: tuple):
        self._network_nodes.append(node)
        self.__network_dirty = True

        if len(self._network_nodes) >= 2:
            projected_nodes = [self.transformer.transform(lon, lat) for lat, lon in self._network_nodes]
            self.geo_route = LineString(projected_nodes)
            self._L = self.geo_route.length / 1000

    def calculate_network(self, points: Points) -> None:
        if self.__network_dirty:
            self.__calculate_network(points)
            self.__network_dirty = False

    @property
    def gravitating(self):
        return self._gravitating

    @property
    def attracting(self):
        return self._attracting

    @property
    def L(self):
        return self._L

    @property
    def K(self):
        return self._K

    @property
    def network_inertia(self):
        return self._network_inertia

    @property
    def all_of_demand_zones_q(self):
        return self._all_of_demand_zones_q

    @property
    def gravitating_demand_zones_area(self):
        return self._gravitating_demand_zones_area

    def __calculate_network(self, points: Points) -> None:
        """
        Calculates inertia by finding the distance from each neighborhood
        center to the nearest point on the transit route.
        """
        if self.geo_route is None:
            return

        self._K = 0
        self._network_inertia = 0
        self._all_of_demand_zones_q = 0
        self._gravitating_demand_zones_area = 0

        for zone, center in points.demand_zone_centers.items():
            lat, lon = center
            q = points.q_in_demand_zone[zone]
            area = points.area_in_demand_zone[zone]
            self._all_of_demand_zones_q += q

            point_m = Point(self.transformer.transform(lon, lat))
            min_dist = self.geo_route.distance(point_m) / 1000

            if min_dist <= self._gravitating:
                self._gravitating_demand_zones_area += area
                self._network_inertia += q * (min_dist ** 2)
                self._K += 1

    # ── Formulas ──────────────────────────────────────────────────────────────

    def formula3(self):
        part1 = (self.K ** 2) * (self.city.area)
        part2 = 2 * (self.city.num_neighborhoods ** 2) * self.gravitating * self.L
        part3 = (self.K ** 3) * (self.attracting ** 2) * self.all_of_demand_zones_q
        part4 = 2 * (self.city.num_neighborhoods ** 3) * self.network_inertia
        return ((part1 / part2) + (part3 / part4)) * 100

    def formula4(self):
        part1 = (self.K ** 2) * self.gravitating_demand_zones_area
        part2 = 2 * (self.city.num_neighborhoods ** 2) * self.gravitating * self.L
        part3 = (self.K ** 2) * (self.attracting ** 2) * self.all_of_demand_zones_q
        part4 = 2 * (self.city.num_neighborhoods ** 2) * self.network_inertia
        return ((part1 / part2) + (part3 / part4)) * 100

    def formula5(self):
        part1 = (self.K ** 2) * self.gravitating_demand_zones_area
        part2 = 2 * (self.city.num_neighborhoods ** 2) * self.gravitating * self.L * self.city.area
        part3 = (self.K ** 2) * (self.attracting ** 2) * self.all_of_demand_zones_q
        part4 = 2 * (self.city.num_neighborhoods ** 2) * self.network_inertia
        return ((part1 / part2) + (part3 / part4)) * 100

    def formula6(self):
        part1 = (self.K ** 2) * self.gravitating * self.L
        part2 = 2 * (self.city.num_neighborhoods ** 2) * self.gravitating_demand_zones_area
        part3 = (self.K ** 2) * (self.attracting ** 2) * self.all_of_demand_zones_q
        part4 = 2 * (self.city.num_neighborhoods ** 2) * self.network_inertia
        return ((part1 / part2) + (part3 / part4)) * 100
