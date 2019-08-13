from biothings_explorer.hint import Hint
import json
from .base import BaseHandler

ht = Hint()


class HintHandler(BaseHandler):
    def get(self):
        _input = self.get_query_argument('q', None)
        if _input:
            result = ht.query(_input)
            self.set_status(200)
            self.write(json.dumps(result))
            self.finish()
        else:
            self.set_status(400)
            self.write(json.dumps({'No input is found'}))
