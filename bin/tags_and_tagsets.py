#!/usr/bin/env python3

import sys
import datetime
import mediacloud
import os
import json
import gzip
import logging

from json import JSONEncoder
from datetime import date, datetime, timedelta
from gensim import corpora

# Give an idea of how long we have to go

from progressbar import ProgressBar, Percentage, Bar, AdaptiveETA

gLogger = logging.getLogger(__file__)
gLogger.setLevel(logging.WARNING)

# Constant definitions

MC_API_KEY = '6f503c700b907b45dd7e0106dd39c3cfe2af11d7f69547341ddc844de7f55e7d'
MC_API_KEY_2 = '0eef9c4d6d2d30b9b4a606e554b4bac388372e1c6075455ec4bfe27d26ecfab4'


    
# Classes

def get_tag_sets():
    last_tag_sets_id = 0
    all_tag_sets = []
    res = mc.tagSetList(rows=100, last_tag_sets_id = last_tag_sets_id)
    while len(res) > 0:
        res = mc.tagSetList(rows=100, last_tag_sets_id = last_tag_sets_id)
        last_tag_sets_id = res[-1]['tag_sets_id']
        all_tag_sets += res

    print("found {} tag sets".format(len(all_tag_sets)))
    return (all_tag_sets)

def get_tags():
    last_tags_id = 0
    all_tags = []
    res = mc.tagList(rows=100, last_tags_id = last_tags_id)
    iteration = 1
    while len(res) > 0:
        res = mc.tagList(rows=100, last_tags_id = last_tags_id)
        last_tags_id = res[-1]['tags_id']
        all_tags += res
        if iteration % 20 == 0:
            print ("On interation #: {}".format(iteration))
        iteration += 1

    print("found {} tags".format(len(all_tag_sets)))
    return (all_tags)

if __name__ == "__main__":
    # Command line interface

    from getopt import *

    # Settable parameters

    gRows = 20
    gOutput = sys.stdout
    gOutputFile = None
    gCorpusFile = None
    gCompress = False
    gQuiet = False
    gTopics = []
    gBiases = []
    gLanguage = 'en'

    errflag = 0

    # Process command line arguments

    # opts, args = getopt(
    #     sys.argv[1:],
    #     'b:c:hl:o:qt:vz?',
    #     ('bias', 'corpus', 'help', 'language', 'output', 'quiet', 'topic', 'verbose', 'compress')
    # )
    opts = []

    for k, v in opts:
        if k in ('-b', '--bias'):
            if v in BIAS_ABBREV:
                v = BIAS_ABBREV[v]

            if v not in BIAS_VALUE:
                gLogger.error('Illegal bias value %s' % v)
                errflag += 1
                continue
            gBiases.append(v)
        elif k in ('-c', '--corpus'):
            gCorpusFile = v
        elif k in ('-h', '--help'):
            errflag += 1
        elif k in ('-o', '--output'):                        # Output file
            gOutputFile = v
        elif k in ('-q', '--quiet'):
            gQuiet = True
        elif k in ('-r', '--rows'):
            gRows = int(v)
        elif k in ('-t', '--topic'):
            gTopics.append(v)
        elif k in ('-v', '--verbose'):
            gLogger.setLevel(gLogger.getEffectiveLevel() - 10)
        elif k in ('-z', '--compress'):
            gCompress = True
        else:
            gLogger.error('Illegal option %s' % k)
            errflag += 1

    # Handle errors or -h.

    if gCompress and not gOutputFile:
        gLogger.error("Can't compress output without an output filename")
        errflag += 1

    if errflag:
        sys.stderr.write("""Usage: %s [-b bias] [-l lang] [-o file] [-t topic] [-q] [-v] [-z]
    -b bias   Use the given bias. May be repeated. Values include:
              - c or center
              - l or left
              - cl or center-left
              - cr or center-right
              - r or right
              If no value is given, all biases are assumed.
    -l lang	  Language to look for. Defaults to 'en'
    -o file   Write JSON output to the specified file
    -c file   Write MM corpus output to the specified file
    -t topic  List of topics to retrieve. May be repeated.
    -h        Print this message
    -q        Quiet output
    -v        Verbose output
    -z        Compress output with gzip
    """ % sys.argv[0])
        sys.exit(1)

    # Handle defaults and post-processing for command line arguments.

    if gOutputFile:
        if os.path.exists(gOutputFile):
            os.rename(gOutputFile, gOutputFile + '~')

        if gCompress:
            gOutput = gzip.open(gOutputFile, mode='wt', encoding='utf-8')
        else:
            gOutput = open(gOutputFile, mode='w', encoding='utf-8')




    mc = mediacloud.api.MediaCloud(MC_API_KEY)

    

    if not mc:
        gLogger.error('Failed to connect to MediaCloud')
        sys.exit(1)


    json.dump(result, gOutput, indent=2, cls=WordMatrix)

    if gCorpusFile:
        corpora.MmCorpus.serialize(gCorpusFile, result.mm())
