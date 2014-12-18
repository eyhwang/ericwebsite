from flask import Flask
from flask import render_template
import os

#schedule_api_consumer_key = 'ZUCbrVGNYplQ707v_ZDAHXSvphUa'
#schedule_api_secret_key   = 'S1q4vypi7pRTIcMq3hlu9jc5pRca'
app = Flask(__name__)
app.secret_key = os.urandom(1337)
app.config['DEBUG'] = True
