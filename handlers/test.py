import json
from .base import BaseHandler


class TestHandler(BaseHandler):
    def get(self):
        _input = self.get_query_argument('q', None)
        print('input is {}'.format(_input))
        if _input:
            self.set_status(200)
            self.write(json.dumps({'your input': _input}))
            self.finish()
        else:
            self.set_status(400)
            self.write(json.dumps({'No input is found'}))