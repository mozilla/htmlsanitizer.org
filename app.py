import os
import bleach
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return show_index()
    return bleach_content()

def show_index(): 
   return render_template('index.html')

def bleach_content():
    return pull_content(request);

def pull_content(request):
    content_type = request.headers.get('Content-Type')
    methods = {
        'application/json': handle_json,
        'application/x-www-form-urlencoded': handle_form
    }
    handler = methods.get(content_type);
    if not handler:
        return "Content-Type must be either application/json or application/x-www-form-urlencoded", 406
    return handler(request)

def handle_json(request):
    return 'lol, json'

def handle_form(request):
    return 'lol, form'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
