
from generic_anova import HandlerMixin

from tornado import (
    gen,
    ioloop,
    web,
)
from . import pid


class SettingResource(web.RequestHandler, HandlerMixin):
    """
    動作確認しながら係数調整するためのAPI
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        kp = self.get_argument("kp", None)
        ki = self.get_argument("ki", None)
        kd = self.get_argument("kd", None)

        if kp:
            pid.Kp = float(kp)

        if ki:
            pid.Ki = float(ki)

        if kd:
            pid.Kd = float(kd)

        self.json_response(dict(kp=pid.Kp, ki=pid.Ki, kd=pid.Kd))
