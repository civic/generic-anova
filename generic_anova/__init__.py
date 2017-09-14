
import json


class HandlerMixin:
    def request_json(self):
        return json.loads(self.request.body.decode('utf8'))

    def json_response(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))
