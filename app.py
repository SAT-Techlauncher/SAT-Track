#!/bin/env python
from server import app
from config import SERVER_HOST, SERVER_PORT

if __name__ == '__main__':
    # start running server
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)