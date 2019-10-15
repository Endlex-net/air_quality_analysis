import math
import traceback
from functools import reduce
from typing import Tuple, List
from abc import ABC, abstractmethod

import settings
from core.coordinate import coordinate_handler
from core.file_server import CSVFile


class Dot:
    """一个数据点"""

    def __init__(self, stationid: str, station_name: str, csv_name: str, x: float, y: float, pm: float):
        self.stationid = stationid
        self.station_name = station_name
        self.csv_name = csv_name  # 所属文件名
        self.pm = float(pm)
        self.x_y = (float(x), float(y))

    @property
    def x(self) -> float:
        return self.x_y[0]

    @property
    def y(self) -> float:
        return self.x_y[1]

    # 给的坐标不是经纬度坐标，而是平面坐标取消转换
    # def set_x_y(self, lon_lat: Tuple[float, float]) -> None:
    #     """设置坐标"""
    #     self.x_y = coordinate_handler.convert(*lon_lat)


class Area:
    """片区"""

    def __init__(self, origin_xy: Tuple[float, float], width: float, height: float):
        self.origin_xy = origin_xy
        self.width = width
        self.height = height
        self.pm = 0
        self.dots = []

    def has_x_y(self, x, y) -> bool:
        """判断坐标是否在区域内"""
        min_x = self.origin_xy[0]
        max_x = min_x + self.width
        min_y = self.origin_xy[1]
        max_y = min_y + self.height
        return min_x < x < max_x and min_y < y < max_y

    def set_dots(self, dots: List[Dot]) -> None:
        """设置区域内的dots"""
        tmp_dots = list(filter(lambda dot: self.has_x_y(*dot.x_y), dots))
        if tmp_dots:
            self.dots = tmp_dots
            self.pm = sum([dot.pm for dot in tmp_dots]) / len(tmp_dots)

    def get_near_area_xys(self):
        """获取临近的area坐标s"""
        near_area_xys = [
            (self.origin_xy[0], self.origin_xy[1] + self.height),
            (self.origin_xy[0], self.origin_xy[1] - self.height),
            (self.origin_xy[0] + self.width, self.origin_xy[1]),
            (self.origin_xy[0] - self.width, self.origin_xy[1]),
            (self.origin_xy[0] - self.width, self.origin_xy[1] - self.height),
            (self.origin_xy[0] + self.width, self.origin_xy[1] - self.height),
            (self.origin_xy[0] - self.width, self.origin_xy[1] + self.height),
            (self.origin_xy[0] + self.width, self.origin_xy[1] + self.height),
        ]
        return near_area_xys


class AreaFactory:
    """片区工厂"""

    def create(self, origin_xy, width, height, dots: List[Dot]):
        area = Area(origin_xy, width, height)
        tmp_dot = list(filter(lambda dot: area.has_x_y(*dot.x_y), dots))
        area.set_dots(tmp_dot)
        if not area.dots:
            area.pm = -1
        return area


area_factory = AreaFactory()


class Map:
    """地图"""
    width = settings.Width
    min_y = settings.MinY
    max_y = min_y + width
    min_x = settings.MinX
    max_x = min_x + width

    slices_count = settings.Slices_Count

    def __init__(self, name):
        self.name = name
        self.dots = []
        self.areas = []
        self.bound = None
        self.background = None

    def append_dot(self, dot: Dot) -> None:
        """增加测量点"""
        # if self.min_x < dot.x_y[0] < self.max_x and self.min_y < dot.x_y[1] < self.max_y:
        #     self.dots.append(dot)
        self.dots.append(dot)

    def create_area(self) -> None:
        """生成片区"""
        width = (self.max_x - self.min_x) / self.slices_count
        height = (self.max_y - self.min_y) / self.slices_count
        area_origin_xys = []
        tmp_x = self.min_x
        tmp_y = self.min_y
        for x in range(self.slices_count):
            for y in range(self.slices_count):
                area_origin_xys.append((tmp_x + width * x, tmp_y + height * y))
        for origin_xy in area_origin_xys:
            area = area_factory.create(origin_xy, width, height, self.dots)
            self.areas.append(area)

    def refresh_area_pm(self) -> None:
        """
            尽可能的更新空pm点的pm值
            通过临近三点以上的area的pm 计算当前片区的pm值
        """
        zero_mp_areas = [area for area in self.areas if area.pm < 0]
        real_mp_areas = [area for area in self.areas if area.pm >= 0]
        for zero_mp_area in zero_mp_areas:
            near_origin_xys = zero_mp_area.get_near_area_xys()
            near_areas = [
                area for area in real_mp_areas for near_origin_xy in near_origin_xys
                if abs(area.origin_xy[0] - near_origin_xy[0]) < 0.0001
                   and abs(area.origin_xy[1] - near_origin_xy[1]) < 0.0001
            ]
            if len(near_areas) >= 3:
                zero_mp_area.pm = sum([a.pm for a in near_areas]) / len(near_areas)


class MapFactory:
    """map工厂"""

    def create(self, csv_file: CSVFile):
        data = csv_file.data
        dots = []
        for row in data:
            try:
                dot = Dot(row[0], row[1], csv_file.name, row[2], row[3], row[4])
                dots.append(dot)
            except:
                print("Warning:")
                traceback.print_exc()

        dots = self.filter_useless_dots(dots)
        map = Map(csv_file.name)
        for dot in dots:
            map.append_dot(dot)
        map.create_area()
        for i in range(settings.ForgeTimes):
            map.refresh_area_pm()
        return map

    def filter_useless_dots(self, dots: List[Dot]):
        """筛选掉特别偏僻的点"""
        dot_count = len(dots)
        center_dot = (sum([dot.x for dot in dots]) / dot_count, sum(dot.y for dot in dots) / dot_count)
        distance_points = lambda x_y1, x_y2: ((x_y1[0] - x_y2[0]) ** 2 + (x_y1[1] - x_y2[1]) ** 2) ** 0.5
        avg_distance = sum([distance_points(dot.x_y, center_dot) for dot in dots]) / dot_count
        variance_distance = lambda x_y1: (distance_points(x_y1, center_dot) - avg_distance) ** 2
        avg_variance = sum([variance_distance(dot.x_y) for dot in dots]) / dot_count
        ret_dots = list(filter(lambda dot: variance_distance(dot.x_y) < avg_variance, dots))
        return ret_dots


map_factory = MapFactory()

if __name__ == "__main__":
    from core.file_server import file_handler

    csv_file = file_handler.get_csv_files()[0]
    map = map_factory.create(csv_file)
    print(len(map.areas))
