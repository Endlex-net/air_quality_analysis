import os
import csv
from typing import List, Iterator

import settings


class FileHandler:
    def __init__(self, DataPath: str):
        self.data_dir_path = DataPath

    def all_files(self) -> Iterator[str]:
        files = os.listdir(self.data_dir_path)
        return filter(lambda x: x.endswith('.csv'), files)

    def get_csv_files(self):
        csv_files = [CSVFile(f"{self.data_dir_path}/{csv_path}") for csv_path in
                     self.all_files()]
        return csv_files


class CSVFile:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)
        self.file_path = file_path
        self.data: List = self.read_file()

    def read_file(self) -> List:
        with open(self.file_path, 'r', encoding='gbk') as f:
            csv_file = csv.reader(f)
            data = [row for row in csv_file if len(row) == 5 and row[4] not in ["pm", "PM25_V"]]
        return data


file_handler = FileHandler(settings.DataPath)

if __name__ == "__main__":
    print(list(file_handler.get_csv_files()))
