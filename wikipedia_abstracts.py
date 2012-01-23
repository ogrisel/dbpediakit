"""Utility script to extract the text abstract of Wikipedia from DBpedia"""
# License: MIT

import os
import re
from urllib import unquote
from bz2 import BZ2File

URL_PATTERN = ("http://downloads.dbpedia.org/"
               "{version}/{lang}/long_abstracts_{lang}.nt.bz2")
VERSION = "3.7"
LANG = "en"
LOCAL_FOLDER = os.path.join("~", "data", "dbpedia")

LINE_PATTERN = re.compile(r'<([^<]+?)> <[^<]+?> "(.*)"@\w\w .\n')


def fetch(lang=LANG, version=VERSION, folder=LOCAL_FOLDER):
    """Fetch the DBpedia abstracts dump and cache it locally"""
    folder = os.path.expanduser(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

    url = URL_PATTERN.format(**locals())
    filename = url.rsplit('/', 1)[-1]
    filename = os.path.join(folder, filename)
    if not os.path.exists(filename):
        print "Downloading %s to %s" % (url, filename)
        # for some reason curl is much faster than urllib2 and has the
        # additional benefit of progress report and streaming the data directly
        # to the hard drive
        cmd = "curl -o %s %s" % (filename, url)
        os.system(cmd)
    return filename


def human_readable(id, prefix="http://dbpedia.org/resource/"):
    return unquote(id[len(prefix):]).replace('_', ' ')


def extract_abstracts(filename, max_items=None, verbose=True):
    """Extract and decode abstracts on the fly

    Return a generator of (id, title, text) triples:
    - id is the raw DBpedia URI of the resource.
    - title that should match the Wikipedia title of the article.
    - text is the first paragraph of the Wikipedia article without any markup.

    """
    reader = BZ2File if filename.endswith('.bz2') else open

    current_line_number = 0
    with reader(filename, 'rb') as f:
        for line in f:
            current_line_number += 1
            if max_items is not None and current_line_number > max_items:
                break
            if verbose and current_line_number % 10000 == 0:
                print "Decoding line %d" % current_line_number
            m = LINE_PATTERN.match(line)
            if m is None:
                if verbose:
                    print ("[WARNING] Invalid line %d, skipping."
                           % current_line_number)
                continue
            id = m.group(1)
            title = human_readable(id)
            text = m.group(2).decode('unicode-escape')
            yield (id, title, text)


if __name__ == "__main__":
    for id, title, text in extract_abstracts(fetch(), max_items=10):
        print "%s\n\n%s\n\n" % (title, text)
