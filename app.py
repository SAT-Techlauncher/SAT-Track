#!/bin/env python
from server import app
from config import conf

if __name__ == '__main__':
    # start running server
    app.run(host=conf.SERVER_HOST, port=conf.SERVER_PORT, threaded=True)