import os
import re
import string
import tempfile
import subprocess
from functools import wraps
from billy.scrape.utils import convert_pdf


def pdfdata_to_text(data):
    with tempfile.NamedTemporaryFile(delete=True) as tmpf:
        tmpf.write(data)
        tmpf.flush()
        return convert_pdf(tmpf.name, 'text')


def worddata_to_text(data):
    _, txtfile = tempfile.mkstemp(prefix='tmp-worddata-', suffix='.txt')
    with tempfile.NamedTemporaryFile(delete=True) as tmpf:
        tmpf.write(data)
        subprocess.check_call('abiword --to=%s %s' % (txtfile, tmpf.name), 
                              shell=True)
        tmpf.flush()
        text = open(txtfile).read()
    os.remove(txtfile)
    return text.decode('utf8')

def text_after_line_numbers(lines):
    text = []
    for line in lines.splitlines():
        # real bill text starts with an optional space, line number
        # more spaces, then real text
        match = re.match('\s*\d+\s+(.*)', line)
        if match:
            text.append(match.group(1))

    # return all real bill text joined w/ newlines
    return '\n'.join(text).decode('utf-8', 'ignore')


PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))


def _clean_text(text):
    text = text.encode('ascii', 'ignore')
    text = text.replace(u'\xa0', u' ') # nbsp -> sp
    text = PUNCTUATION.sub(' ', text)  # strip punctuation
    text = re.sub('\s+', ' ', text)    # collapse spaces
    return text


def oyster_text(function):
    @wraps(function)
    def wrapper(oyster_doc, data):
        return _clean_text(function(oyster_doc, data))
    return wrapper