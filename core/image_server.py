from matplotlib import pyplot

import settings


class Image:
    """图像画布"""

    def __init__(self, name: str):
        self.name = name
        self.fig = pyplot.figure(self.name)
        self.board = self.fig.add_subplot()
        width = settings.Width
        min_y = settings.MinY
        min_x = settings.MinX
        pyplot.ylim((min_y, min_y + width))
        pyplot.xlim((min_x, min_x + width))
        pyplot.axis('scaled')

    def draw_dot(self, x, y, color=None):
        """在图上画点"""
        if color:
            self.board.scatter(x, y, c=color)
        else:
            self.board.scatter(x, y)

    def draw_area(self, x, y, width, height, color=None):
        """在图上画区域"""
        if color:
            rect = pyplot.Rectangle((x, y), width, height, color=color)
        else:
            rect = pyplot.Rectangle((x, y), width, height)
        self.board.add_patch(rect)

    def show(self):
        """预览"""
        pyplot.show()

    def save_img(self):
        """保存图片"""
        save_path = f"{settings.SavePath}/{self.name}.png"
        pyplot.savefig(save_path)


if __name__ == "__main__":
    image = Image("demo")
    image.draw_dot(1, 2)
    image.draw_dot(2, 2)
    image.draw_dot(2, 3)

    image.show()
