import timeit, numpy
from src.common_utils.constants import RGBColors

from src.common_utils.models import Point, Vector
import src.common_utils.cv_drawing as drawing_utils


def compare_functions(func1: str, func2: str, iterations=1000):
    func1_time = timeit.timeit(func1, number=iterations)
    func2_time = timeit.timeit(func2, number=iterations)

    print(f"Function1 Speed: {func1_time}\nFunction2 Speed: {func2_time}\n"
          + f"Time difference = {numpy.abs(func1_time - func2_time)}")


def cv2_vector_test():
    import cv2
    image = cv2.imread('C:\\Users\\Cactus\\Pictures\\Aldor foothills.PNG')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    start_point = Point(100, 100)
    p2 = Point(700, 400)
    v = Vector.from_points(start_point, p2)
    drawing_utils.draw_line_from_vector(image, start_point, v, drawing_utils.RGBColors.GREEN)
    drawing_utils.draw_line_from_points(image, start_point, p2, drawing_utils.RGBColors.RED)

    # Get assumption
    dest_x = int(start_point.x + v.magnitude * numpy.cos(v.direction))
    dest_y = int(start_point.y + v.magnitude * numpy.sin(v.direction))
    pt2 = Point(dest_x, dest_y)

    drawing_utils.draw_line_from_points(image, p2, pt2, drawing_utils.RGBColors.YELLOW)
    drawing_utils.draw_node(image, p2, True, False)
    drawing_utils.draw_node(image, pt2, False, True)

    cv2.imshow('test', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyWindow('test')

def test_access_dict(d: dict):
    test = d.get("8888")

def test_iter_list(l: list):
    for i in range(0, len(l)):
        if list[i] == "8888":
            return list[i]


if __name__ == "__main__":
    d = {}
    for i in range(0, 10000):
        d[str(i)] = i
    l = [str(x) for x in range(0, 10000)]
    compare_functions(lambda : test_iter_list(l), lambda : test_access_dict(d), iterations=10000)
