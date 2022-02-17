import numpy as np
import datetime


def reMap(value, maxInput, minInput, maxOutput, minOutput):

    value = maxInput if value > maxInput else value
    value = minInput if value < minInput else value

    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput

    scaledThrust = float(value - minInput) / float(inputSpan)

    return minOutput + (scaledThrust * outputSpan)


res = reMap(5, 10, 0, 1000, 0)


points = [
    [0, 69],
    [2, 72],
    [4, 68],
    [6, 73],
    [8, 78],
    [10, 85],
    [12, 82],
    [14, 81],
    [16, 88],
    [18, 98],
    [20, 96],
    [22, 82],
    [24, 69],
]


x = list()
y = list()

for point in points:
    x.append(point[0])
    y.append(reMap(point[1], 98, 68, 3.2, 1.2))


coefficients = np.polyfit(x, y, 9)
poly = np.poly1d(coefficients)

dt = datetime.datetime.now()
h = dt.hour
m = dt.minute

dec_time = (h * 60 + m) / 60
res = poly(dec_time)

print(dec_time, res)


points_solar = [
    [0, 0],
    [2, 0],
    [4, 0],
    [6, 0.3],
    [8, 1.25],
    [10, 2.75],
    [12, 3.7],
    [13, 3.75],
    [14, 3.4],
    [16, 2.6],
    [18, 1],
    [20, 0.25],
    [22, 0],
    [24, 0],
]
x = list()
y = list()
for point in points_solar:
    x.append(point[0])
    y.append(point[1])


coefficients_solar = np.polyfit(x, y, 8)
poly_solar = np.poly1d(coefficients_solar)


print(dec_time, res)
