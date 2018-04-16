from bs4 import BeautifulSoup    # Library for manipulating (e.g. scraping) web pages
                                 # Used here to get the text of the news storys without
                                 # the html markup
import pandas as pd
import glob
import sys
import parse
from io import BytesIO
import pycurl
import re
import datetime

TEMPLATE = """
<doc id="{doc_id}">
 <topic>{topic}</topic>
 <headline><![CDATA[{headline}]]></headline>
 <bias>{wing}</bias>
 <url><![CDATA[{url}]]></url>
 <text><![CDATA[{story_text}]]></text>
 <date>{date}</date>
 </doc>
"""
start = datetime.datetime.now()
sources = glob.glob('*-?-*.csv')
headers = {'Accept-Encoding': 'deflate'}

if len(sources) == 0:
    print('Need a file with -l- or -r- in its name.  got {}'.format(args.infile))
    sys.exit(-1)
print('<docs>')
for s in sources:
    wordcount = 0
    urlcount = 0
    topic, wing, rest = parse.parse('{}-{}-{}', s)
    sys.stderr.write('doing csv {}\n'.format(s))
    wing = wing.upper()
    thisdf = pd.read_csv(s)
    for idx, row in thisdf.iterrows():
        ##sys.stderr.write('\tdoing row {}, title {}\n'.format(idx, row['title']))  ## uncomment to print out progress (row and title of each  story)
        the_text = None
        
        c = pycurl.Curl()
        buffer = BytesIO()
        c.setopt(c.URL, row['url'])
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)   
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.perform()
        c.close()
        the_text = buffer.getvalue()
        soup = BeautifulSoup(the_text, 'html.parser')  # This next bit cleans up the
                                                            # content of the story
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        txt = soup.get_text()
        print(TEMPLATE.format(doc_id = row['stories_id'], topic=topic,
                              headline = row['title'].encode("ascii", errors="ignore").decode(),
                              wing=wing, url=row['url'],
                              story_text = txt.encode("ascii", errors="ignore").decode(),
                              date=row['publish_date']))
        urlcount += 1
        wordcount += len(re.findall(r'\w+', txt))

        #except:
        #    sys.stderr.write('\n*****\nfailed for csv: {}, row{}, title: {}, url: {}\n*****\n'.format(
        #        s,idx, row['title'].encode("ascii", errors="ignore").decode(),
        #                                                             row['url']))
    sys.stderr.write('Topic: {topic}, bias: {bias} had {wordcount} words in {urlcount} stories\n'.format(
            topic = topic, bias = wing, wordcount = wordcount, urlcount = urlcount))
print('</docs>')
