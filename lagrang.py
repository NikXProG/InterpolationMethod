from abc import ABC, abstractmethod
import json
import numpy as np
import matplotlib.pyplot as plt


class ReadInfoService:

    def __init__(self, reader_service):
        self.reader_service = reader_service

    def get_info(self):
        return self.reader_service.read()


class IReaderService(ABC):
    @abstractmethod
    def read(self, path_file):
        """reading from some data format or console"""


class JsonReaderService(IReaderService):

    def __init__(self, path):
        self.f = open(path, 'r')

    def read(self):
        return json.load(self.f)

    def __del__(self):
        self.f.close()


#for further implementation
class ParserGridService:

    def __init__(self, data):
        self.data = data

    def parse(self):
        lst = []
        for key in self.data:
            if key == "x":
                if self.data[key]["array"] is not None:
                    lst.append(self.data[key]["array"])
                else:
                    range_lst = []
                    ub = self.data[key]["range"]["upper bound"]
                    lb = self.data[key]["range"]["lower bound"]
                    stp = self.data[key]["range"]["step"]
                    if ub <= lb and stp > (ub - lb):
                        raise Exception("invalid range")
                    for item in np.arange(lb, ub + stp, stp):
                        range_lst.append(float(item))
                    lst.append(range_lst)
            else:
                lst.append(self.data[key])
        return lst


class IInterpolationMethodService(ABC):
    @abstractmethod
    def interpolate(self, data):
        """realization methods of interpolation"""


class LagrangeMethod(IInterpolationMethodService):

    def __init__(self, data):
        if not data or len(data) < 3 or any(item is None for item in data[:3]):
            raise Exception("Value cannot be None: the drawing service needs to determine the coordinates xi, yi, "
                            "x and obtain an approximation of the points using interpolation methods.")
        self.xi = data[0]
        self.yi = data[1]
        self.x = data[2]

    def interpolate(self):
        approx_points = []
        n = len(self.xi)
        count_point = len(self.x)

        if n != len(self.yi):
            raise Exception("Invalid grid function: count point xi not equal to count point yi")

        for point_i in range(count_point):
            polonium = 0.0
            for i in range(n):
                l_basis = 1.0
                for j in range(n):
                    if i != j:
                        l_basis *= (self.x[point_i] - self.xi[j]) / (self.xi[i] - self.xi[j])
                polonium += l_basis * self.yi[i]
            approx_points.append(polonium)

        return [self.x, approx_points]


class PaintService:
    def __init__(self, data):
        if not data or len(data) < 2 or any(item is None for item in data[:2]):
            raise Exception("Value cannot be None")
        self.data_x = data[0]
        self.approx_points = data[1]

    def paint(self):
        plt.plot(self.data_x, self.approx_points)
        plt.show()


if __name__ == '__main__':
    reader = ReadInfoService(JsonReaderService("file.json"))
    parser = ParserGridService(reader.get_info())
    result = LagrangeMethod(parser.parse()).interpolate()
    PaintService(result).paint()
