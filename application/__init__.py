from flask import Flask

app = Flask('application')
app.config['DEBUG'] = False

import views