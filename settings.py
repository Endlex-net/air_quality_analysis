import os

BasePath = os.path.dirname(__file__)
BaseMapPath = BasePath + '/base_map.ipg'
DataPath = BasePath + "/data"
SavePath = BasePath + "/output"
Slices_Count = 25

# MinX = 103.58
# MinY = 35.83
# Width = 0.4
MinX = 102.85
MinY = 35.78
Width = 1.35
ForgeTimes = 35  # 渲染填充未知点次数

if __name__ == "__main__":
    print(BasePath)
    print(BaseMapPath)
