import html5lib
from nose.tools import eq_

import bleach

def doc(fragment = '', head_fragment=''):
    return u'<html><head>%s</head><body>%s</body></html>' % (head_fragment, fragment)

def eq_cleaning_for_frag_and_doc(clean, dirty, head_fragment='', options = dict()):
    """
    Test the cleaning of the dirty fragment both as a fragment and as part

    of a full document

    clean - The expected output
    dirty - The fragment to clean
    options - A dictionary that will be passed as arguments to the clean

        function

    """

    options['parse_as_fragment'] = True
    eq_(clean, bleach.clean(dirty, **options))
    options['parse_as_fragment'] = False
    eq_(doc(clean), bleach.clean(doc(dirty, head_fragment=head_fragment), **options))

def test_doc():
    eq_(doc(''), bleach.clean('', parse_as_fragment=False))

def test_empty():
    eq_cleaning_for_frag_and_doc('', '')

def test_comments_only():
    comment = '<!-- this is a comment -->'
    open_comment = '<!-- this is an open comment'
    eq_('', bleach.clean(comment))
    eq_('', bleach.clean(open_comment))
    eq_(comment, bleach.clean(comment, strip_comments=False))
    eq_('%s-->' % open_comment, bleach.clean(open_comment,
                                             strip_comments=False))

def test_with_comments():
    html = '<!-- comment -->Just text'
    eq_('Just text', bleach.clean(html))
    eq_cleaning_for_frag_and_doc('Just text', html)
    eq_cleaning_for_frag_and_doc(html, html, options={'strip_comments':False})

def test_no_html():
    eq_cleaning_for_frag_and_doc('no html string', bleach.clean('no html string'))

def test_allowed_html():
    html = 'an <strong>allowed</strong> tag'
    eq_cleaning_for_frag_and_doc(html, html)

    html = 'another <em>good</em> tag'
    eq_cleaning_for_frag_and_doc(html, html)

    html = "<blockquote>I've never let my schooling interfere with my education -- Mark Twain</blockquote>"
    eq_cleaning_for_frag_and_doc(html, html)

def test_bad_html():
    fixed_tag = 'a <em>fixed tag</em>'
    unclosed_tag = 'a <em>fixed tag'

    eq_cleaning_for_frag_and_doc(fixed_tag, unclosed_tag)

    safe = 'a &lt;style&gt;body{}&lt;/style&gt; test'
    overriding = 'a <style>body{}</style> test'
    eq_cleaning_for_frag_and_doc(safe, bleach.clean(overriding))

def test_function_arguments():
    TAGS = ['span', 'br']
    ATTRS = {'span': ['style']}

    clean = 'a <br><span style="">test</span>'
    dirty = 'a <br/><span style="color:red">test</span>'

    eq_(clean, bleach.clean(dirty, tags=TAGS, attributes=ATTRS))
    eq_(doc(clean), bleach.clean(doc(dirty), tags=(TAGS + bleach.ALLOWED_BASE_FULL_DOCUMENT_TAGS), attributes=ATTRS, parse_as_fragment=False))

def test_named_arguments():
    ATTRS = {'a': ['rel', 'href']}
    s = u'<a href="http://xx.com" rel="alternate">xx.com</a>'

    eq_cleaning_for_frag_and_doc('<a href="http://xx.com">xx.com</a>', s)

    eq_cleaning_for_frag_and_doc(s, s, options={'attributes':ATTRS})
    print '--'
    eq_cleaning_for_frag_and_doc(
        u'<a href="http://xx.com" rel="nofollow">xx.com</a>',

        u'<a href="http://xx.com">xx.com</a>',

        options={'attributes':ATTRS, 'nofollow':True})

def test_nofollow():
    eq_cleaning_for_frag_and_doc(
        u'<a href="http://xx.com" rel="nofollow">xx.com</a>',

        u'<a href="http://xx.com">xx.com</a>',

        options={'nofollow':True})

    eq_cleaning_for_frag_and_doc(
        u'<a href="http://xx.com" rel="nofollow">xx.com</a>',

        u'<a href="http://xx.com" rel="xxxx">xx.com</a>',

        options={'nofollow':True})

def test_nofollow_is_independant_of_cleaning():
    eq_cleaning_for_frag_and_doc(
        u'<a href="http://xx.com" rel="nofollow">xx.com</a>',

        u'<a href="http://xx.com" rel="xxxx">xx.com</a>',

        options={'attributes':{'a':['href']}, 'nofollow':True})

def test_disallowed_html():
    safe = 'a &lt;script&gt;safe()&lt;/script&gt; test'
    unsafe = 'a <script>safe()</script> test'

    eq_cleaning_for_frag_and_doc(safe, unsafe)

    safe = 'a &lt;style&gt;body{}&lt;/style&gt; test'
    overriding = 'a <style>body{}</style> test'

    eq_cleaning_for_frag_and_doc(safe, overriding)

def test_bad_href():
    eq_cleaning_for_frag_and_doc('<em>no link</em>', '<em href="fail">no link</em>')

def test_bare_entities():
    eq_cleaning_for_frag_and_doc('an &amp; entity', 'an & entity')
    eq_cleaning_for_frag_and_doc('an &lt; entity', 'an < entity')
    eq_cleaning_for_frag_and_doc('tag &lt; <em>and</em> entity',

        'tag < <em>and</em> entity')
    eq_cleaning_for_frag_and_doc('&amp;', '&amp;')

def test_escaped_entities():
    s = u'&lt;em&gt;strong&lt;/em&gt;'
    eq_cleaning_for_frag_and_doc(s, s)

def test_serializer():
    s = u'<table></table>'
    eq_(s, bleach.clean(s, tags=['table']))
    eq_(doc(s), bleach.clean(doc(s), tags=bleach.ALLOWED_BASE_FULL_DOCUMENT_TAGS + ['table'], parse_as_fragment=False))

    eq_(u'test<table></table>', bleach.linkify(u'<table>test</table>'))

    eq_(u'<p>test</p>', bleach.clean(u'<p>test</p>', tags=['p']))

def test_no_href_links():
    s = u'<a name="anchor">x</a>'
    eq_(s, bleach.linkify(s))

def test_weird_strings():
    s = '</3'
    eq_cleaning_for_frag_and_doc('', s)

def test_xml_render():
    parser = html5lib.HTMLParser()
    eq_(bleach._render(parser.parseFragment('')), '')

def test_stripping():
    eq_cleaning_for_frag_and_doc('a test <em>with</em> <b>html</b> tags',
        'a test <em>with</em> <b>html</b> tags', options={'strip': True})

    eq_cleaning_for_frag_and_doc('a test <em>with</em>  <b>html</b> tags',
        'a test <em>with</em> <img src="http://example.com/"> '
                '<b>html</b> tags', options={'strip':True})

    s = '<p><a href="http://example.com/">link text</a></p>'
    eq_('<p>link text</p>', bleach.clean(s, tags=['p'], strip=True))
    eq_(doc('<p>link text</p>'), bleach.clean(doc(s), tags=['p'] + bleach.ALLOWED_BASE_FULL_DOCUMENT_TAGS, strip=True, parse_as_fragment=False))

    s = '<p><span>multiply <span>nested <span>text</span></span></span></p>'
    eq_('<p>multiply nested text</p>', bleach.clean(s, tags=['p'], strip=True))

    s = ('<p><a href="http://example.com/"><img src="http://example.com/">'
         '</a></p>')
    eq_('<p><a href="http://example.com/"></a></p>',
        bleach.clean(s, tags=['p', 'a'], strip=True))

def test_allowed_styles():
    ATTR = ['style']
    STYLE = ['color']
    blank = '<b style=""></b>'
    s = '<b style="color: blue;"></b>'
    eq_cleaning_for_frag_and_doc(blank, '<b style="top:0"></b>', options={'attributes':ATTR})
    eq_cleaning_for_frag_and_doc(s, s, options={'attributes':ATTR, 'styles':STYLE})
    eq_cleaning_for_frag_and_doc(s, '<b style="top: 0; color: blue;"></b>',
                        options={'attributes':ATTR, 'styles':STYLE})

def test_idempotent():
    """Make sure that applying the filter twice doesn't change anything."""
    dirty = u'<span>invalid & </span> < extra http://link.com<em>'

    clean = bleach.clean(dirty)
    eq_(clean, bleach.clean(clean))

    clean = bleach.clean(doc(dirty))
    eq_(clean, bleach.clean(clean))

    linked = bleach.linkify(dirty)
    eq_(linked, bleach.linkify(linked))

def test_lowercase_html():
    """We should output lowercase HTML."""
    dirty = u'<EM CLASS="FOO">BAR</EM>'
    clean = u'<em class="FOO">BAR</em>'
    eq_cleaning_for_frag_and_doc(clean, dirty, options={'attributes':['class']})

def test_wildcard_attributes():
    ATTRS = {
        '*': ['id'],
        'img': ['src'],
    }
    TAGS = ['img', 'em']
    dirty = (u'both <em id="foo" style="color: black">can</em> have '
             u'<img id="bar" src="foo"/>')
    clean = u'both <em id="foo">can</em> have <img id="bar" src="foo">'

    eq_(clean, bleach.clean(dirty, tags=TAGS, attributes=ATTRS))
    eq_(doc(clean),

        bleach.clean(doc(dirty),

        tags=TAGS + bleach.ALLOWED_BASE_FULL_DOCUMENT_TAGS,

        attributes=ATTRS,
        parse_as_fragment=False))

def test_sarcasm():
    """Jokes should crash.<sarcasm/>"""
    dirty = u'Yeah right <sarcasm/>'
    clean = u'Yeah right &lt;sarcasm/&gt;'
    eq_cleaning_for_frag_and_doc(clean, dirty)

def test_full_document_with_doctype():
    dirty = (u'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Title of This Web Page</title></head><body><p>My first web page.</p></body></html>')
    clean = (u'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Title of This Web Page</title></head><body><p>My first web page.</p></body></html>')
    TAGS = ['html', 'head', 'meta', 'title', 'body', 'p']
    ATTRS = {
      'html':['lang'],
      'meta':['charset'],
    }
    eq_(clean, bleach.clean(dirty, tags=TAGS, attributes=ATTRS, parse_as_fragment=False))
    eq_(clean, bleach.clean(dirty, tags=TAGS + ['DOCTYPE'], attributes=ATTRS, parse_as_fragment=False))

