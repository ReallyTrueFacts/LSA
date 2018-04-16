#!/usr/bin/env python3

import re                                 # For pattern matching
import os                                 # File path munging
import sys                                # Command line args
import logging                            # Debugging output
import gzip                               # Compressing output

# Python library for Web requests, it is used both to get the stories
# from the feed and to interact with the fakebox service

import requests      

# Library for manipulating (e.g. scraping) web pages.  Used here to
# get the text of the news storys without the html markup

from bs4 import BeautifulSoup    

# HTML parsing library used by beautiful soup

import html5lib                  
import pandas as pd
import glob

gLogger = logging.getLogger(__file__)
gLogger.setLevel(logging.WARNING)

TEMPLATE = """
 <doc id="{doc_id}">
  <topic>{topic}<topic/>
  <headline>{headline}</headline>
  <bias>{wing}</bias>
  <url>{url}</url>
  <text>{story_text}</text>
  <date>{date}</date>
 </doc>
"""

# Process command-line args

from getopt import *
gInputDir = "."
gOutput = sys.stdout
gOutputFile = None
gCompress = False
errflag = 0

opts, args = getopt(
    sys.argv[1:],
    'd:o:vz?',
    ('dir', 'output', 'verbose', 'compress')
)

for k, v in opts:
    if k == "-o":                   # Output file
        gOutputFile = v
    elif k == "-d":
        gInputDir = v
    elif k == "-v":
        gLogger.setLevel(gLogger.getEffectiveLevel() - 10)
    elif k == "-z":
        gCompress = True
    else:
        errflag += 1

if errflag:
    sys.stderr.write("Usage: %s [-d dir] [-o file] [-z] [-v]")
    sys.exit(1)

if gOutputFile:
    if os.path.exists(gOutputFile):
        os.rename(gOutputFile, gOutputFile + "~")

    gOutput = open(gOutputFile, mode="wb")

    if gCompress:
        gOutput = gzip.open(gOutput, mode="wb")

# Grab the sources from the input directory

sources = glob.glob(os.path.join(gInputDir, '*-[lr]-stories*.csv'))

if len(sources) == 0:
    gLogger.fatal("No files found")
    sys.exit(1)

pat = re.compile("(?P<topic>[^-]+)-(?P<wing>[lr])-stories-(?P<date>[0-9]+).csv")

gOutput.write(b"<docs>\n")

for s in sources:
    m = pat.match(s)

    wing = m.group('wing')
    topic = m.group('topic')

    thisdf = pd.read_csv(s)

    for idx, row in thisdf.iterrows():
        gLogger.info("Processing file %d" % idx)

        story = requests.get(row['url'])                    # get the story  
        soup = BeautifulSoup(story.content, 'html.parser')  # This next bit cleans up the
                                                            # content of the story
        for script in soup(["script", "style"]):
            script.extract()                                # rip it out
        txt = soup.get_text()
        params = {
            'doc_id': row['stories_id'],
            'headline': row['title'].encode("ascii", errors="ignore").decode(),
            'wing': wing,
            'topic': topic,
            'url': row['url'],
            'story_text': txt.encode("ascii", errors="ignore").decode(),
            'date': row['publish_date']
        }
        gOutput.write(TEMPLATE.format(**params).encode('utf-8'))

gOutput.write(b"</docs>\n")
