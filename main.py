import random
import time
import tago
import numpy as np
import datetime


ACCOUNT_TOKEN = "0acd0e15-bb51-43df-9f5c-968bf0c1292a"
TAGO_ACCOUNT = tago.Account(ACCOUNT_TOKEN)


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


class TagoDevice:
    def __init__(self, name: str):
        self.name = name
        if not self.find_device(name):
            self.create_device(name)

    def find_device(self, name: str):

        devices = TAGO_ACCOUNT.devices.list()["result"]
        for dev in devices:
            if dev["name"] == name:
                self.id = dev["id"]
                self.token = TAGO_ACCOUNT.devices.tokenList(self.id)["result"][-1][
                    "token"
                ]
                self.device = tago.Device(self.token)
                return True
        return False

    def create_device(self, name: str):
        new_device = {
            "name": name,
            "description": f"SIOT device.",
            "active": True,
            "visible": True,
            "tags": [{"key": "type", "value": "siot"}],
        }
        result = TAGO_ACCOUNT.devices.create(new_device)["result"]
        self.id = result["device_id"]
        self.token = result["token"]
        self.device = tago.Device(self.token)


def main():

    solar_poly = get_solar_polynomial()
    house_poly = get_house_polynomial()

    number_of_devices = 10
    devices_list = list()
    # * Crear u obtener los dispositivos
    for n in range(0, number_of_devices):
        devices_list.append(TagoDevice(name=f"SIOT-DEVICE-{n}"))
        devices_list[n].co2 = round(random.uniform(5, 60), 2)
        devices_list[n].euros = round(devices_list[n].co2 * 3.2, 2)
        devices_list[n].oil = round(devices_list[n].co2 * 0.0029, 2)
        devices_list[n].trees = int(devices_list[n].co2 * 2.43)
        devices_list[n].day = None
        devices_list[n].cont = random.randint(1, 500)

        devices_list[n].device.insert({"variable": "co2", "value": devices_list[n].co2})
        devices_list[n].device.insert(
            {"variable": "euros", "value": devices_list[n].euros}
        )
        devices_list[n].device.insert(
            {"variable": "trees", "value": devices_list[n].trees}
        )
        devices_list[n].device.insert({"variable": "oil", "value": devices_list[n].oil})

    while True:
        dt = datetime.datetime.now()
        h = dt.hour
        m = dt.minute
        dec_time = (h * 60 + m) / 60
        for td in devices_list:
            td.cont += 1
            if dt.day != td.day:
                td.day = dt.day
                td.cont += 1  # * Randomize data
                td.time_random_param = random.uniform(-0.1, 0.1)
                if random.randint(1, 3) == 1:
                    td.house_random_param = random.uniform(0.8, 1.2)
                else:
                    td.house_random_param = random.uniform(0.9, 1.1)
                if random.randint(1, 3) == 1:
                    td.solar_random_param = random.uniform(0.6, 1.2)
                else:
                    td.solar_random_param = random.uniform(0.8, 1.2)

            x_time = random.gauss(dec_time, 0.2 + td.time_random_param)
            avg_house_consumption = td.house_random_param * house_poly(x_time)
            avg_solar_generation = td.solar_random_param * solar_poly(x_time)

            house_consumption = round(random.gauss(avg_house_consumption, 0.03), 2)
            solar_generation = round(random.gauss(avg_solar_generation, 0.03), 2)
            if solar_generation < 0:
                solar_generation = 0
            grid_consumption = (
                house_consumption - solar_generation
            )  # Si negativo se consume de la red, si p
            if grid_consumption < 0:
                grid_inyection = abs(grid_consumption)
                grid_consumption = 0
            else:
                grid_inyection = 0

            td.device.insert(
                {"variable": "house_consumption", "value": house_consumption}
            )
            td.device.insert(
                {"variable": "solar_generation", "value": solar_generation}
            )
            td.device.insert(
                {"variable": "grid_consumption", "value": grid_consumption}
            )
            td.device.insert({"variable": "grid_inyection", "value": grid_inyection})

            if td.cont % 50 == 0:
                td.co2 += 0.01
                td.euros += 0.02
                td.device.insert({"variable": "co2", "value": td.co2})
                td.device.insert({"variable": "euros", "value": td.euros})
            if td.cont % 80 == 0:
                td.trees += 1
                td.device.insert({"variable": "trees", "value": td.trees})
            if td.cont % 2000 == 0:
                td.oil += 0.01
                td.device.insert({"variable": "oil", "value": td.oil})

            print(f"{td.name} Updated!")

        # ! Cada 5 min
        print("----------------------------------------------")
        time.sleep(300)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
