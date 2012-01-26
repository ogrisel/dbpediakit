"""Utility script to tweak the ntriples DBpedia dumps"""
# License: MIT

import csv
import logging
import os
import sys
import re
from collections import namedtuple
from urllib import unquote
from bz2 import BZ2File


# use stderr for progress monitoring to be able to use stdout for piping CSV
# stream to postgresql for instance
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format='%(levelname)s\t%(asctime)s\t%(message)s')

URL_PATTERN = ("http://downloads.dbpedia.org/"
               "{version}/{lang}/{archive_name}_{lang}.nt.bz2")
VERSION = "3.7"
LANG = "en"
LOCAL_FOLDER = os.path.join("~", "data", "dbpedia")

TEXT_LINE_PATTERN = re.compile(r'<([^<]+?)> <[^<]+?> "(.*)"@(\w\w) .\n')
LINK_LINE_PATTERN = re.compile(r'<([^<]+?)> <([^<]+?)> <([^<]+?)> .\n')


article = namedtuple('article', ('id', 'title', 'text', 'lang'))
link = namedtuple('link', ('source', 'target'))


def fetch(archive_name, lang=LANG, version=VERSION, folder=LOCAL_FOLDER):
    """Fetch the DBpedia abstracts dump and cache it locally

    Archive name is the filename part without the language, for instance:
      - long_abstracts to be parsed with extract_text
      - skos_categories to be parsed with extract_link

    """
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


def extract_link(archive_filename, max_items=None, predicate_filter=None,
                 strip_prefix="http://dbpedia.org/resource/",
                 max_id_length=300):
    """Extract link information on the fly

    Predicate filter can be a single string or a collection of strings
    to filter out triples that don't match.

    Return a generator of link(source, target) named tuples.

    """
    reader = BZ2File if archive_filename.endswith('.bz2') else open

    current_line_number = 0
    extracted = 0

    if predicate_filter is not None:
        if isinstance(predicate_filter, basestring):
            predicate_filter = set([predicate_filter])
        else:
            predicate_filter = set(predicate_filter)

    with reader(archive_filename, 'rb') as f:
        for line in f:
            current_line_number += 1
            if max_items is not None and extracted > max_items:
                break
            if current_line_number % 100000 == 0:
                logging.info("Decoding line %d", current_line_number)
            m = LINK_LINE_PATTERN.match(line)
            if m is None:
                if TEXT_LINE_PATTERN.match(line) is None:
                    logging.warn("Invalid line %d, skipping.",
                                 current_line_number)
                continue
            predicate = m.group(2)
            if (predicate_filter is not None
                and not predicate in predicate_filter):
                continue
            source = m.group(1)
            target = m.group(3)
            if strip_prefix is not None:
                source = source[len(strip_prefix):]
                target = target[len(strip_prefix):]
            if (max_id_length is not None
                and (len(source) > max_id_length
                     or len(target)> max_id_length)):
                logging.warn("Skipping line %d, with len(source) = %d and"
                             " len(target) = %d",
                             current_line_number, len(source), len(target))
                continue

            yield link(source, target)
            extracted += 1


def extract_text(archive_filename, max_items=None, min_length=300,
                 strip_prefix="http://dbpedia.org/resource/",
                 max_id_length=300):
    """Extract and decode text literals on the fly

    Return a generator of article(id, title, text) named tuples:
    - id is the raw DBpedia id of the resource (without the resource prefix).
    - title is the decoded id that should match the Wikipedia title of the
      article.
    - text is the first paragraph of the Wikipedia article without any markup.
    - lang is the language code of the text literal

    """
    reader = BZ2File if archive_filename.endswith('.bz2') else open

    current_line_number = 0
    extracted = 0

    with reader(archive_filename, 'rb') as f:
        for line in f:
            current_line_number += 1
            if max_items is not None and extracted > max_items:
                break
            if current_line_number % 100000 == 0:
                logging.info("Decoding line %d", current_line_number)
            m = TEXT_LINE_PATTERN.match(line)
            if m is None:
                if LINK_LINE_PATTERN.match(line) is None:
                    logging.warn("Invalid line %d, skipping.",
                                 current_line_number)
                continue
            id = m.group(1)
            if strip_prefix:
                id = id[len(strip_prefix):]
            if (max_id_length is not None and len(id) > max_id_length):
                logging.warn("Skipping line %d, with id with length %d",
                             current_line_number, len(id))
                continue
            title = unquote(id).replace('_', ' ')
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

    logging.info("Dumping tuples as text files in %s", target_folder)
    for _, title, text in tuples:
        filename = title.replace('/', ' ') + ".txt"
        filename = os.path.join(target_folder, filename)
        with open(filename, 'wb') as f:
            f.write(text)
            f.write("\n")


def dump_as_csv(tuples, output, end_marker=None):
    """Extract archives entries as a single CSV file

    output can be a filename or a file-like object such as stdout.
    """
    def write_csv(f):
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        for tuple in tuples:
            writer.writerow(tuple)
        if end_marker is not None:
            f.write(end_marker)
        f.flush()

    if hasattr(output, 'write'):
        write_csv(output)
    else:
        with open(output, 'wt') as f:
            write_csv(f)
