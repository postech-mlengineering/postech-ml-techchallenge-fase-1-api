import logging
from api.__init__ import create_app

#o logger principal foi configurado em api/__init__.py
logger = logging.getLogger('api')

app = create_app()

if __name__ == '__main__':
    #a chamada db.create_all() já está dentro do create_app()
    app.run(debug=True)