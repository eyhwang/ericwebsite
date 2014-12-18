from app import app
from views import *
from flask import Flask, render_template, request, url_for

if __name__ == '__main__':
    app.run(debug=True)