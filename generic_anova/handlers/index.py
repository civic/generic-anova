from generic_anova import HandlerMixin

from tornado import (
    gen,
    ioloop,
    web,
)
from .pid import pid_model
from .temperature import temp_model


class IndexHandler(web.RequestHandler, HandlerMixin):

    @gen.coroutine
    def get(self):
        """
        初期表示データのレスポンス
        :return:
        """

        self.json_response(dict(
            control_state=pid_model.control_state,
            target_temperature=pid_model.target,
            chart_data = list(temp_model.fetch_all()),
            current_temperature=temp_model.current,
            set_hours=pid_model.set_hours,
            set_minutes=pid_model.set_minutes,
            past_seconds=pid_model.past_seconds,
            left_seconds=pid_model.left_seconds,
            end_time=pid_model.end_time.isoformat() if pid_model.end_time else None,
            power=pid_model.power
        ))



