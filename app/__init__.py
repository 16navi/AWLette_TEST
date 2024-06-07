from flask import Flask

app = Flask(__name__)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

from app import routes

app.run(debug=True)