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


class NewtonMethod(IInterpolationMethodService):

    def __init__(self, data):
        if not data or len(data) < 3 or any(item is None for item in data[:3]):
            raise Exception("Value cannot be None: the drawing service needs to determine the coordinates xi, yi, "
                            "x and obtain an approximation of the points using interpolation methods.")
        self.xi = data[0]
        self.yi = data[1]
        self.x = data[2]
        self.divided_differences = self.calculate_divided_differences()

    def calculate_divided_differences(self):
        n = len(self.xi)
        divided_diff = np.zeros((n, n))
        divided_diff[:, 0] = self.yi

        for j in range(1, n):
            for i in range(n - j):
                divided_diff[i][j] = (divided_diff[i + 1][j - 1] - divided_diff[i][j - 1]) / (self.xi[i + j] - self.xi[i])

        return divided_diff

    def interpolate(self):
        approx_points = []
        count_point = len(self.x)

        for point_i in range(count_point):
            x_value = self.x[point_i]
            polynomial = self.divided_differences[0][0]
            product = 1.0

            for j in range(1, len(self.xi)):
                product *= (x_value - self.xi[j - 1])
                polynomial += self.divided_differences[0][j] * product

            approx_points.append(polynomial)

        return [self.x, approx_points]

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
                    if self.xi[i] - self.xi[j] == 0:
                        # Invalid grid function:  empty dot
                        # xj and xi form zero and an error occurs ZeroDivisionError
                        continue
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

    def paint(self, title = '' , color = 'gray'):

        plt.plot(self.data_x ,self.approx_points, color = color)
        plt.title(title)
        plt.show()


if __name__ == '__main__':
    reader = ReadInfoService(JsonReaderService("file.json"))
    parser = ParserGridService(reader.get_info())
    result_lagr = LagrangeMethod(parser.parse()).interpolate()
    result_newton = NewtonMethod(parser.parse()).interpolate()
    PaintService(result_newton).paint(color='orange', title='Интерполяция Ньютона')
    PaintService(result_lagr).paint(color='lightblue',title='Интерполяция Лагранжа')
