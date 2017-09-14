from tornado import (
    gen,
    options,
)
import re
import time
import datetime
from distutils.util import strtobool



try:
    import RPi.GPIO as GPIO
except:
    class DummyGPIO:
        BCM=1
        OUT=2
        def output(self, a,b):pass
        def setup(self, a,b):pass
        def setmode(self, a):pass
    GPIO = DummyGPIO()


class GPIOController:
    def __init__(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)
        GPIO.output(5, 0)

    @gen.coroutine
    def output(self, power, collect_sec):
        on_seconds = power / 10
        off_seconds = 10 - on_seconds

        on_seconds += collect_sec[0]
        on_seconds = max(on_seconds, 0.0)

        off_seconds += collect_sec[1]
        off_seconds = max(off_seconds, 0.0)

        if on_seconds > 0:
            gen.app_log.debug("GPIO ON %.2f seconds. (%.2fs)", on_seconds,collect_sec[0])
            GPIO.output(5, 1)
            yield gen.sleep(on_seconds)

        if off_seconds > 0:
            gen.app_log.debug("GPIO OFF %.2f seconds. (%.2fs)", off_seconds,collect_sec[1])
            GPIO.output(5, 0)
            yield gen.sleep(off_seconds)


class OneWireSensor:
    def __init__(self, device_id, dummy=False):
        self.device_id = device_id
        self.current_value = None

        if dummy:
            self.read_temperature_sensor_value = self.dummy_reader

    def read_temperature_sensor_value(self):
        with open("/sys/bus/w1/devices/%s/w1_slave" % self.device_id) as w1:
            m = re.search(r't=(.*)$', w1.readlines()[1])
            if m:
                self.current_value = int(m.group(1)) / 1000 + 0.4   #0.4はキャリブレーションで出した値
                return

        self.current_value = None


    def dummy_reader(self):
        from .handlers.pid import pid_model
        import random


        if self.current_value is None:
            self.current_value = 40
            self.buffer_power = 0
        else:
            t = (datetime.datetime.now() - self.__time).seconds

            self.buffer_power = max(self.buffer_power-t*3, 0)
            self.buffer_power = min(300, self.buffer_power + pid_model.power)
            self.current_value += t*self.buffer_power / 10000

            self.current_value -= t * 0.02


        self.__time = datetime.datetime.now()
        return self.current_value



class PollingSensorValueCollector:
    def __init__(self):
        dummy_gpio = strtobool(options.options['dummy_gpio'])
        self.one_wire_sensors = {
            "water": OneWireSensor(options.options['water_mac'], dummy_gpio),
            "board": OneWireSensor(options.options['board_mac'], dummy_gpio),
        }


    def collect(self):
        for name, sensor in self.one_wire_sensors.items():
            sensor.read_temperature_sensor_value()
            gen.app_log.debug("1Wire Read: %s=%f", name, sensor.current_value)

    def get_value(self, name):
        return self.one_wire_sensors[name].current_value


