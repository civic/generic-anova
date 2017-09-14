from generic_anova import HandlerMixin

from tornado import (
    gen,
    web,
    options,
)
import datetime
import collections
import requests

Kp = 20
Ki = 0.2
Kd = 10.00

class PIDModel:
    def __init__(self):
        self.control_state = 'stop'
        self.target = 60.0
        self.set_hours = 2
        self.set_minutes = 20

        self.start_time = None
        self.end_time = None

        self.power = 0
        self.history = collections.deque(maxlen=18)
        self.alarmed_time = None

    def start_control(self, hours, minutes):
        if (self.control_state != 'stop' and self.control_state != 'pause'):
            return

        if self.control_state == 'stop':
            # stop->start
            self.start_time = datetime.datetime.now()

        self.set_hours = hours
        self.set_minutes = minutes

        self.end_time =self.start_time + datetime.timedelta(hours=hours, minutes=minutes)

        self.control_state = 'start'

    def pause_control(self):
        if self.control_state != 'start':
            return
        self.control_state = 'pause'

    def stop_control(self):
        self.control_state = 'stop'

    @property
    def past_seconds(self):
        if self.start_time:
            return (datetime.datetime.now() - self.start_time).seconds
        else:
            return 0

    @property
    def left_seconds(self):
        now = datetime.datetime.now()
        if self.end_time and self.end_time > now:
            return (self.end_time - now).seconds
        else:
            return 0

    def check_alarm(self):
        if self.alarmed_time != self.end_time and self.end_time <= datetime.datetime.now():
            self.alarmed_time = self.end_time
            gen.app_log.info("Alarmed!!")
            requests.post('https://maker.ifttt.com/trigger/ganova/with/key/'+options.options['ifttt_api_key'],
                          json=dict(value1=str(self.alarmed_time)))


    def update_power(self, current_temperature):

        self.history.append(dict(t=datetime.datetime.now(), v=current_temperature))

        if self.control_state == "start":

            def p_control(current, target):
                return (target - current) * Kp

            def i_control(history, target):
                area = 0

                prev_t = None
                prev_v = None
                for history_row in history:
                    t = history_row['t']
                    v = history_row['v']

                    if prev_t is not None:
                        area += ((target-prev_v) + (target-v)) * (t - prev_t).seconds /2

                    prev_t = t
                    prev_v = v

                return area * Ki

            def d_control(history, target):
                if len(history) > 2 :
                    de = (target - history[-1]['v']) - (target - history[-2]['v']) - \
                         ((target - history[-2]['v']) - (target - history[-3]['v']))
                else:
                    return 0

                return de * Kd


            p = p_control(current_temperature, self.target)
            i = i_control(self.history, self.target)
            d = d_control(self.history, self.target)

            non_limit_power = p + i + d

            gen.app_log.debug("v=%.2f\t p=%.2f\t i=%.2f\t d=%.2f\t power=%.2f",
                              current_temperature, p, i, d, non_limit_power)

            self.power = int(max(min(non_limit_power, 100), 0))

        else:
            self.power = 0

        return self.power


class PIDResource(web.RequestHandler, HandlerMixin):

    @gen.coroutine
    def get(self):

        self.json_response({
            'control_state': pid_model.control_state,
            'target_temperature': pid_model.target,
            'set_hours': pid_model.set_hours,
            'set_minutes': pid_model.set_minutes,
            'past_seconds': pid_model.past_seconds,
            'left_seconds': pid_model.left_seconds,
            'end_time': pid_model.end_time.isoformat() if pid_model.end_time else None,
            'power': pid_model.power,
        })

    @gen.coroutine
    def put(self):
        params = self.request_json()

        if 'control_state' in params:
            if params['control_state'] == 'start':
                pid_model.start_control(params['set_hours'], params['set_minutes'])

            elif params['control_state'] == 'pause':
                pid_model.pause_control()

            elif params['control_state'] == 'stop':
                pid_model.stop_control()

        if 'target_temperature' in params:
            pid_model.target = params['target_temperature']

        self.get()


pid_model = PIDModel()
