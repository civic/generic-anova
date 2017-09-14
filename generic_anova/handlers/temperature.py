from generic_anova import HandlerMixin

from tornado import (
    gen,
    ioloop,
    web,
)
import datetime
from .pid import pid_model
import sqlite3
import os
import pathlib

class TemperatureModel:
    def __init__(self):

        initdb = not pathlib.Path('ganova.db').exists()
        self.db = sqlite3.connect('ganova.db')

        if initdb:
            self.db.execute("""
            CREATE TABLE history(
                t text primary key,
                w_val real,
                b_val real,
                power real
                )
            """)

        self.delete_old_data()

    def delete_old_data(self):
        # 2日以上経過したデータは不要
        self.db.execute("DELETE FROM history WHERE t < ?",
                        ((datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),))
        self.db.commit()

    def clear(self):
        self.db.execute("DELETE FROM history")
        self.db.commit()

    @property
    def current(self):
        c = self.db.cursor()
        try:
            for w_val, in c.execute("SELECT w_val FROM history ORDER BY t desc LIMIT 1"):
                return w_val
        finally:
            c.close()


        return None

    def add_new_temperature(self, water_temperature, board_temperature):
        newdata = {"t": datetime.datetime.now().isoformat(),
                   "y1": water_temperature,
                   "y2": board_temperature,
                   "p": pid_model.power,
                }

        self.db.execute("INSERT INTO history(t, w_val, b_val, power) VALUES(?, ?, ?, ?)",
                        (newdata['t'], water_temperature, board_temperature, pid_model.power))
        self.db.commit()

        return newdata

    def fetch_all(self):
        c = self.db.cursor()
        try:
            for t, w_val, b_val, power in c.execute("SELECT * FROM history ORDER BY t"):
                yield {
                   "t": t,
                   "y1": w_val,
                   "y2": b_val,
                   "p": power,
                }
        finally:
            c.close()

temp_model = TemperatureModel()

class TemperatureResource(web.RequestHandler, HandlerMixin):
    def get(self):
        pass

    @gen.coroutine
    def delete(self):
        temp_model.clear()
        self.json_response({})

