# /run.py
import os
#from dotenv import load_dotenv, find_dotenv
from flask import Flask, current_app, render_template
from .src.appinit import create_app
#load_dotenv(find_dotenv())

env_name = 'local'
app = create_app(env_name)



if __name__ == '__main__':

  # run app
  app.run(host='0.0.0.0', port=5000)