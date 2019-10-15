import math
from typing import Tuple
from geopy.geocoders import Nominatim


class CoordinateHandler:
    def __init__(self):
        self.convertion = MillierConvertion()

    def convert(self, lon: float, lat: float):
        """坐标转换"""
        return self.convertion.convert(lon, lat)


class MillierConvertion:
    """米勒投影"""
    pi = 3.14159265358979323846
    L = 6381372 * pi * 2  # 地球周长(x轴的坐标)
    H = L / 2  # y轴约等于周长一半

    def convert(self, lon: float, lat: float) -> Tuple[float, float]:
        """将经纬度坐标转化为平面坐标"""
        mill = 2.3
        x = lon * self.pi / 180
        y = lat * self.pi / 180

        y = 1.25 * math.log(math.tan(0.25 * self.pi + 0.4 * y))

        x = (self.L / 2) + (self.L / (2 * self.pi)) * x
        y = (self.H / 2) - (self.H / (2 * mill)) * y
        return (x, y)


coordinate_handler = CoordinateHandler()

if __name__ == "__main__":
    lon_lat_list = [
        (103.843931, 36.052076),
        (103.843994, 36.052046),
        (103.852511, 36.054504),
    ]
    for lon_lat in lon_lat_list:
        print(coordinate_handler.convert(*lon_lat))
