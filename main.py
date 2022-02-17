import random
import time
import tago
import numpy as np
import datetime

device_token = "f8d2036c-833f-46a5-ba52-bc3d2c8988aa"
device = tago.Device(device_token)


def reMap(value, maxInput, minInput, maxOutput, minOutput):

    value = maxInput if value > maxInput else value
    value = minInput if value < minInput else value

    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput

    scaledThrust = float(value - minInput) / float(inputSpan)

    return minOutput + (scaledThrust * outputSpan)


def get_house_polynomial():
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
    return poly


def get_solar_polynomial():
    points = [
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
    for point in points:
        x.append(point[0])
        y.append(point[1])

    coefficients = np.polyfit(x, y, 8)
    poly = np.poly1d(coefficients)
    return poly


def main():

    solar_poly = get_solar_polynomial()
    house_poly = get_house_polynomial()

    # Invent
    co2 = 37.32
    euros = 133.43
    oil = 0.01
    trees = 17

    cont = 0

    while True:

        dt = datetime.datetime.now()
        h = dt.hour
        m = dt.minute
        dec_time = (h * 60 + m) / 60

        x_time = random.gauss(dec_time, 0.2)
        avg_house_consumption = house_poly(x_time)
        avg_solar_generation = solar_poly(x_time)

        house_consumption = round(random.gauss(avg_house_consumption, 0.03), 2)
        solar_generation = round(random.gauss(avg_solar_generation, 0.03), 2)

        grid_consumption = (
            house_consumption - solar_generation
        )  # Si negativo se consume de la red, si p
        if grid_consumption < 0:
            grid_inyection = abs(grid_consumption)
            grid_consumption = 0
        else:
            grid_inyection = 0

        device.insert({"variable": "house_consumption", "value": house_consumption})
        device.insert({"variable": "solar_generation", "value": solar_generation})
        device.insert({"variable": "grid_consumption", "value": grid_consumption})
        device.insert({"variable": "grid_inyection", "value": grid_inyection})

        if cont % 100 == 0:
            co2 += 0.01
            euros += 0.02
            device.insert({"variable": "co2", "value": co2})
            device.insert({"variable": "euros", "value": euros})
        if cont % 500 == 0:
            trees += 1
            device.insert({"variable": "trees", "value": trees})
        if cont % 10000 == 0:
            oil += 0.01
            device.insert({"variable": "oil", "value": oil})

        cont += 1
        print("sent")
        time.sleep(60)


if __name__ == "__main__":
    main()
