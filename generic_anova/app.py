import pathlib

from tornado import (
    gen,
    ioloop,
    web,
    options,
)

from generic_anova.handlers import (
    TemperatureResource,
    PIDResource,
    SSEHandler,
    IndexHandler,
    publisher,
    SettingResource,
)
from generic_anova.handlers.pid import pid_model
from generic_anova.handlers.temperature import temp_model

from generic_anova.device import GPIOController, PollingSensorValueCollector
import datetime
import logging
from logging.handlers import RotatingFileHandler

def make_app(static_dir=None):
    if static_dir is None:
        static_dir = "./static"

    static_path = pathlib.Path(static_dir).as_posix()

    app = web.Application([
        (r'/api/index', IndexHandler),
        (r'/api/temperature', TemperatureResource),
        (r'/api/pid', PIDResource),
        (r'/api/setting', SettingResource),
        (r'/sse', SSEHandler),
        (r'/(.*)', web.StaticFileHandler, {"path": static_path, "default_filename": "index.html"})
    ])

    return app

class Controller:
    @gen.coroutine
    def __call__(self):
        # GPIO, 温度収集モジュール生成
        gpio_controller = GPIOController()
        collector = PollingSensorValueCollector()

        # データ用のログハンドラ準備
        data_log = logging.getLogger("datalog")
        data_log.setLevel(logging.INFO)
        handler1 = RotatingFileHandler(filename="ganova.log", backupCount=3, maxBytes=2*1024*1024)
        handler1.setFormatter(logging.Formatter("%(message)s"))
        data_log.addHandler(handler1)

        while True:
            # 現在温度をセンサーから計測
            collect_start_time = datetime.datetime.now()
            collector.collect()

            w_temperature = collector.get_value("water")
            b_temperature = collector.get_value("board")
            newdata = temp_model.add_new_temperature(w_temperature, b_temperature)

            # 温度計測に数秒かかるのでその分を加熱・冷却時間に加味する
            delta = (datetime.datetime.now() - collect_start_time)
            collect_seconds = delta.seconds + delta.microseconds / 1000000.0

            gen.app_log.debug("collect seconds=%.3fs", collect_seconds)
            if pid_model.power >= 100:
                diff = (-collect_seconds, 0)    #加熱時間を減らす
            else:
                diff = (0, -collect_seconds)    #停止時間を減らす

            # pid制御用温度を更新
            pid_model.update_power(temp_model.current)


            # SSEへのpublish
            publisher.publish({
                "event": "newdata",
                "data": newdata,
                'past_seconds': pid_model.past_seconds,
                'power': pid_model.power,
            })
            data_log.info("{time}\t{t1:.3f}\t{t2:.3f}\t{power}\t{target}".format(
                time=newdata["t"],
                t1=newdata["y1"],
                t2=newdata["y2"],
                power=pid_model.power,
                target=pid_model.target))

            # 通知チェック
            pid_model.check_alarm()

            yield gpio_controller.output(pid_model.power, diff)


def parse_config():
    options.define("port", default=800, type=int)
    options.define("water_mac", type=str)
    options.define("board_mac", type=str)
    options.define("ifttt_api_key", type=str)
    options.define("dummy_gpio", type=str, default="true")
    options.parse_config_file("ganova.conf")
    for k, v in options.options.items():
        print("%s=%s" % (k, v))

def main():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-4s %(message)s")

    parse_config()

    app = make_app()
    app.listen(options.options['port'])

    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda : gen.app_log.info("Start server localhost:8000"))
    io_loop.call_later(0, Controller())

    io_loop.start()


if __name__ == "__main__":
    main()
