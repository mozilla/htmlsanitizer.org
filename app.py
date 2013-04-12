import os
import bleach
import json
from flask import Flask, render_template, jsonify, request, make_response

VALID_OPTIONS = {
    'text': str,
    'tags': list,
    'attributes': dict,
    'styles': list,
    'strip': bool,
    'strip_comments': bool,
    'parse_as_fragment': bool
}

DEFAULT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true'
}

BAD_CONTENT_TYPE = "Content-Type must be either application/json or application/x-www-form-urlencoded"
BAD_JSON = "Could not parse request. Make sure your JSON is valid"
BAD_FORM = "Could not read form data."
MISSING_REQUIRED_TEXT = "Didn't find any text to bleach. Make sure you pass a value for `text` in your JSON object"
INVALID_OPTION_TYPES = "Some options have an invalid type. Make sure you're sending strings, lists, dicts and bools in the appropriate places"
BLEACH_ERROR = "Something went wrong passing options to bleach. Please check your input and try again"

app = Flask(__name__)

def respond(data, headers={}, status=200):
    response = make_response(data);
    for (key, value) in DEFAULT_HEADERS.items():
        response.headers[key] = value
    for (key, value) in headers.items():
        response.headers[key] = value
    response.status_code = status
    print "wooble: " + status
    return response


def respond_with_error(msg, status=400):
    return respond(msg, status)

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
        return respond_with_error(BAD_CONTENT_TYPE, status=406)
    return handler(request)

def handle_json(request):
    body = request.data
    try:
        options = json.loads(body)
    except ValueError, e:
        return respond_with_error(BAD_JSON)
    return sanitize(options, 'json')

def handle_form(request):
    if not request.form:
        return respond_with_error(BAD_FORM)
    return sanitize(request.form, 'form')

def sanitize(options, content_type):
    if not options.get('text'):
        return respond_with_error(MISSING_REQUIRED_TEXT)
    options = remove_invalid_options(options)
    if not options_are_valid(options):
        return respond_with_error(INVALID_OPTION_TYPES)
    try:
        response = bleach.clean(**options)
        return respond(response)
    except:
        return respond_with_error(BLEACH_ERROR)

def remove_invalid_options(options):
    valid_options = {}
    for opt in VALID_OPTIONS.keys(): 
        value = options.get(opt)
        if value is not None:
            valid_options[opt] = value
    return valid_options

def options_are_valid(options):
    for (option, correct_type) in VALID_OPTIONS.items():
        if not VALID_OPTIONS.get(option) == correct_type:
            return False
    attr = options.get('attributes')
    tags = options.get('tags')
    styles = options.get('styles')
    if (attr and not attributes_are_valid(attr)) or \
       (tags and not tags_are_valid) or \
       (styles and not styles_are_valid(styles)):
        return False
    return True
   
def attributes_are_valid(attributes):
    for value in attributes.values():
        if type(value) != list:
            return False
    return True

def tags_are_valid(tags):
    for value in tags:
        if type(value) != str:
            return False
    return True

styles_are_valid = tags_are_valid


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if (os.environ.get("DEBUG")):
        app.debug = True
    app.run(host='0.0.0.0', port=port)
