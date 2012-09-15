from nose.tools import assert_false, assert_true
import app

def test_valid_attributes():
    attrs = {'strong': ['title'], 'script': ['async']}
    assert_true(app.attributes_are_valid(attrs))

def test_invalid_attributes():
    attrs = {'strong': 'title', 'script': 'async'}
    assert_false(app.attributes_are_valid(attrs))

def test_valid_tags():
    tags = ['strong', 'b', 'em', 'i']
    assert_true(app.tags_are_valid(tags))

def test_invalid_tags():
    tags = [{}, [], False]
    assert_false(app.tags_are_valid(tags))

def test_valid_styles():
    styles = ['color', 'background', 'opacity']
    assert_true(app.styles_are_valid(styles))

def test_invalid_styles():
    styles = [{}, [], False]
    assert_false(app.styles_are_valid(styles))

