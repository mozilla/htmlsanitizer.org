import os
import bleach
import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

VALID_OPTIONS = [
    'text',
    'tags',
    'attributes',
    'styles',
    'strip',
    'strip_comments'
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return show_index()
    return handle_post()

def show_index(): 
   return render_template('index.html')

def handle_post():
    return parse_request(request);

def parse_request(request):
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
    body = request.data
    try:
        options = json.loads(body)
    except ValueError, e:
        return "Could not parse request. Make sure your JSON is valid", 400
    return sanitize(options, 'json')

def handle_form(request):
    if not request.form:
        return "Could not read form data.", 400
    return sanitize(request.form, 'form')

def sanitize(options, content_type):
    if not options.get('text'):
        return "Didn't find any text to bleach. Make sure you pass a value for `text` in your JSON object", 400
    options = remove_invalid_options(options)
    return bleach.clean(**options)

def remove_invalid_options(options):
    valid_options = {}
    for opt in VALID_OPTIONS: 
        value = options.get(opt)
        if value:
            valid_options[opt] = value
    return valid_options

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if (os.environ.get("DEBUG")):
        app.debug = True
    app.run(host='0.0.0.0', port=port)
