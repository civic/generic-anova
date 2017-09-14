import pytest
import freezegun
import datetime

from generic_anova.device import OneWireSensor
from generic_anova.handlers.pid import pid_model

def test_sensor():
    sensor = OneWireSensor("a", True)

    with freezegun.freeze_time("2017/09/10 10:00:00"):
        assert sensor.read_temperature_sensor_value() == 30

    with freezegun.freeze_time("2017/09/10 10:00:01"):
        assert sensor.read_temperature_sensor_value() == 29.95

    with freezegun.freeze_time("2017/09/10 10:00:10"):
        assert sensor.read_temperature_sensor_value() == 29.5


def test_sensor_power():
    sensor = OneWireSensor("a", True)

    with freezegun.freeze_time("2017/09/10 10:00:00"):
        assert sensor.read_temperature_sensor_value() == 30

    pid_model.power = 100
    with freezegun.freeze_time("2017/09/10 10:00:01"):
        assert sensor.read_temperature_sensor_value() == 29.96


    with freezegun.freeze_time("2017/09/10 10:00:02"):
        assert sensor.read_temperature_sensor_value() == 29.96 +0.0198 - 0.05

    d = datetime.datetime(2017, 9, 10, 10, 1, 2)

    for _ in range(60):
        d += datetime.timedelta(seconds=1)
        with freezegun.freeze_time(d):
            print(sensor.read_temperature_sensor_value())
