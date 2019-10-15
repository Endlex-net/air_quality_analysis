from abc import ABC, abstractmethod

from core.file_server import file_handler
from core.image_server import Image
from models import Dot, Map, MapFactory, Area


class ColorSelect(ABC):
    @abstractmethod
    def color(self, area: Area):
        pass


class DotCountColorSelect(ColorSelect):
    """依据区域内节点个数提供颜色"""

    def color(self, area: Area):
        dot_count = len(area.dots)
        if dot_count == 0:
            color = "k"
        elif dot_count <= 5:
            color = "g"
        elif dot_count <= 10:
            color = "y"
        else:
            color = "b"
        return color


class DotPmValueColorSelect(ColorSelect):
    """依据区域内的pm_value提供颜色"""

    def color(self, area: Area):
        pm = area.pm
        colors = [
                     "#cc0000", "#cc1100", "#cc2200", "#cc3300", "#cc4400", "#cc5500", "#cc6600", "#cc7700",
                     "#cc8800", "#cc9900", "#ccaa00", "#ccbb00", "#cccc00", "#bbcc00", "#aacc00", "#99cc00",
                     "#88cc00", "#77cc00", "#66cc00", "#55cc00", "#44cc00", "#33cc00", "#22cc00", "#11cc00",
                     "#00cc00",
                 ][::-1]
        values = range(5, 101, 100 // len(colors))
        value_color_list = list(zip(values, colors))

        if pm < 0:
            return "#ffffff"

        for value_color in value_color_list:
            if pm < value_color[0]:
                return value_color[1]


if __name__ == "__main__":
    csv_files = file_handler.get_csv_files()
    for csv_file in csv_files:
        map_factory = MapFactory()
        map = map_factory.create(csv_file)
        image = Image(map.name)

        color_select = DotPmValueColorSelect()

        # # 打印点
        # for dot in map.dots:
        #     color = color_select.color(dot)
        #     image.draw_dot(*dot.x_y, color=color)

        # 打印区域
        for area in map.areas:
            color = color_select.color(area)
            image.draw_area(*area.origin_xy, area.width, area.height, color=color)

        image.save_img()  # 保存图
        # image.show()  # 展示图
