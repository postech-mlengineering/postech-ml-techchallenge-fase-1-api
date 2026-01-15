import logging
from api.__init__ import create_app


logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
