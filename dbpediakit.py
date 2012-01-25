"""Utility script to tweak the ntriples DBpedia dumps"""
# License: MIT

import os
import re
import csv
from collections import namedtuple
from urllib import unquote
from bz2 import BZ2File

URL_PATTERN = ("http://downloads.dbpedia.org/"
               "{version}/{lang}/{archive_name}_{lang}.nt.bz2")
VERSION = "3.7"
LANG = "en"
LOCAL_FOLDER = os.path.join("~", "data", "dbpedia")

TEXT_LINE_PATTERN = re.compile(r'<([^<]+?)> <[^<]+?> "(.*)"@(\w\w) .\n')


article = namedtuple('article', ('id', 'title', 'text', 'lang'))
link = namedtuple('link', ('source', 'target'))


def fetch(archive_name, lang=LANG, version=VERSION, folder=LOCAL_FOLDER):
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


def extract_text(filename, max_items=None, min_length=300, verbose=True):
    """Extract and decode text literals on the fly

    Return a generator of article(id, title, text) named tuples:
    - id is the raw DBpedia URI of the resource.
    - title that should match the Wikipedia title of the article.
    - text is the first paragraph of the Wikipedia article without any markup.
    - lang is the language code of the text literal

    """
    reader = BZ2File if filename.endswith('.bz2') else open

    current_line_number = 0
    extracted = 0

    with reader(filename, 'rb') as f:
        for line in f:
            current_line_number += 1
            if max_items is not None and extracted > max_items:
                break
            if verbose and current_line_number % 10000 == 0:
                print "Decoding line %d" % current_line_number
            m = TEXT_LINE_PATTERN.match(line)
            if m is None:
                if verbose:
                    print ("[WARNING] Invalid line %d, skipping."
                           % current_line_number)
                continue
            id = m.group(1)
            title = human_readable(id)
            text = m.group(2).decode('unicode-escape')
            if len(text) < min_length:
                continue
            lang = m.group(3)
            yield article(id, title, text, lang)
            extracted += 1


def dump_as_files(tuples, target_folder):
    """Extract archives entries as independent text files"""
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for _, title, text in tuples:
        filename = title.replace('/', ' ') + ".txt"
        filename = os.path.join(target_folder, filename)
        with open(filename, 'wb') as f:
            f.write(text)
            f.write("\n")


def dump_as_csv(tuples, output):
    """Extract archives entries as a single CSV file

    output can be a filename or a file-like object such as stdout.
    """

    def write_csv(f):
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        for tuple in tuples:
            writer.writerow(tuple)

    if hasattr(output, 'write'):
        write_csv(output)
    else:
        with open(output, 'wt') as f:
            write_csv(f)
