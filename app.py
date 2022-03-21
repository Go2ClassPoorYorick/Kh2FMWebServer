from asyncio.windows_events import NULL
import random
import os
from flask import Flask, render_template, request, url_for
from routes.abilities import abilityApi
#Crude method to add an API key, I am uncertain how secure this may be considered. If the debug environmental variable = "true" this functionality is disabled.

apiKey = os.environ.get('apiKey') or ''.join(random.choice('0123456789ABCDEF') for i in range(16))
print(apiKey)



# People like to assume that a server has to have some webpage- we provide one, and an elementary interface for manually interacting with the api.
# This isn't reccomended.(especially because it isn't finished)
app = Flask(__name__)
@app.before_request
def before_request():
    if os.environ.get('debug') != "true":
        if request.args.get('apiKey') != apiKey:
            return "Missing or Incorrect API KEY", 401

#Loads the ability API functionality
app.register_blueprint(abilityApi)

@app.route('/')
def home():
    return render_template('home.html', apiKey=request.args.get('apiKey'))

with app.test_request_context():
    print('http://localhost:5000'+url_for('home',apiKey=apiKey))

if __name__ == '__main__':
    app.run(...)