# /run.py
import os

from flask import Flask, current_app, render_template
from src.appinit import create_app


env_name = 'local'
app = create_app(env_name)

#app = Flask(__name__)

#@app.route('/')
#def get():
#  return {'hello': 'world1'}

#migrate:     flask db migrate --directory migrationsDev
#upgrade:     flask db upgrade --directory migrationsDev

if __name__ == '__main__':

  # run app
  app.run(debug=True,host='0.0.0.0',port=5000)