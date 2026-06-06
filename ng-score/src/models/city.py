from dataclasses import dataclass


@dataclass
class City:
    name: str
    area: float
    hood_borders: list
    hood_population: list
    area_for_each_neighborhood: list

    @property
    def num_neighborhoods(self) -> int:
        return len(self.area_for_each_neighborhood)
