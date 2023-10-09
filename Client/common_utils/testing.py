import timeit, numpy


def compare_functions(func1: str, func2: str, iterations=1000):
    func1_time = timeit.timeit(func1, number=iterations)
    func2_time = timeit.timeit(func2, number=iterations)

    print(f"Function1 Speed: {func1_time}\nFunction2 Speed: {func2_time}\n"
          + f"Time difference = {numpy.abs(func1_time - func2_time)}")
