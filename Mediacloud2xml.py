import requests      # Python library for Web requests, 
                     #   it is used both to get the stories from the feed
                     #   and to interact with the fakebox service
from bs4 import BeautifulSoup    # Library for manipulating (e.g. scraping) web pages
                                 # Used here to get the text of the news storys without
                                 # the html markup
import html5lib                  # html parsing library used by beautiful soup
import pandas as pd
import glob
import sys
import parse

TEMPLATE = """
<doc id={doc_id}>
 <topic>{topic}<topic/>
 <headline>{headline}</headline>
 <bias>{wing}<bias/>
 <url>{url}<url />
 <text>{story_text}</text>
 <date>{date}</date>
 </doc>
"""

sources = glob.glob('*-?-*.csv')
headers = {'Accept-Encoding': 'deflate'}

if len(sources) == 0:
    print('Need a file with -l- or -r- in its name.  got {}'.format(args.infile))
    sys.exit(-1)
print('<docs>')
for s in sources:
    topic, wing, rest = parse.parse('{}-{}-{}', s)
    sys.stderr.write('doing csv {}\n'.format(s))
    wing = wing.upper()
    thisdf = pd.read_csv(s)
    for idx, row in thisdf.iterrows():
        ##sys.stderr.write('\tdoing row {}, title {}\n'.format(idx, row['title']))  ## uncomment to print out progress (row and title of each  story)
        try:
            story= requests.get(row['url'], headers=headers)     # get the story  
            soup = BeautifulSoup(story.content, 'html.parser')  # This next bit cleans up the
                                                                # content of the story
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            txt = soup.get_text()
            print(TEMPLATE.format(doc_id = row['stories_id'], topic=topic,
                                  headline = row['title'].encode("ascii", errors="ignore").decode(),
                                  wing=wing, url=row['url'], story_text = txt.encode("ascii", errors="ignore").decode(),
                                  date=row['publish_date']))
        except:
            sys.stderr.write('\n*****\nfailed for csv: {}, row{}, title: {}, url: {}\n*****\n'.format(s,idx,
                row['title'].encode("ascii", errors="ignore").decode(),
                                                                     row['url']))
print('</docs>')
