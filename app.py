import tornado.httpserver
import tornado.ioloop
import tornado.web

from handlers.functional_sim import FunctionalSimilarityHandler
from handlers.protein_interaction import ProteinInteractionHandler
from handlers.hint import HintHandler
from handlers.test import TestHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/v1/func_sim", FunctionalSimilarityHandler),
            (r"/api/v1/protein_interact", ProteinInteractionHandler),
            (r"/api/v1/query", HintHandler),
            (r"/api/v1/test", TestHandler)
        ]

        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    app.listen(8855)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
