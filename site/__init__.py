from flask import Flask

app = Flask('site')
app.config['DEBUG'] = True

import views