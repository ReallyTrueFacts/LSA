import sys
import datetime

import mediacloud, json, datetime
MC_API_KEY = '6f503c700b907b45dd7e0106dd39c3cfe2af11d7f69547341ddc844de7f55e7d'
mc = mediacloud.api.MediaCloud(MC_API_KEY)

TOPICS = ['cats', 'pruitt', 'skripal']
COLLECTIONS = {'center': 9360522,
               'left': 9360520,
               'center-left': 9360521,
               'center-right': 9360523,
               'right': 9360524}
#TOPIC=['pruitt']
#COLLECTIONS={'right': 9360524}
now = datetime.date.today()
fetch_size = 20
#
#This is a sample of the output
#
TEMPLATE = """
[{
 "run_date": "2018-04-20",
 "topic": "cats",
 "collection_name": "left",
 "collection_id": 9360520,
 "stories": [
   {
     "story_id": 1234,
     "url" : "https://www.brietbart.com/story1",
     "pub_date": "2018-01-01",
     "headline" : "Good stuff here"
   },
   { "story_id": "another story" }
   ],
   "word_list" : [["list", "list"], ["of", "of"], ["words", "words"]],
   "word_matrix": { {"12345": {"1": 27, "4": 12, "33": 8}}, {"78910": {"2": 16, "23": 9, "42": 11}}}

}
,
]
"""
result_list = []
start = datetime.datetime.now()
today = datetime.date.today()
wing_dict = {'left': -2, 'center-left': -1, 'center': 0, 'center-right': 1, 'right': 2}

print('')
for t in TOPICS:
    for c in COLLECTIONS.keys():
        this_query = {
            "run_date": start,
            "topic": t,
            "collection": c,
            "collection_id": COLLECTIONS[c],
            "wing": c,
            }
        
        sys.stderr.write('doing topic {} collection {}\n'.format(t,c))
        wing = wing_dict[c]

        #wm = mc.storyWordMatrix('{}'.format(t), solr_filter=[
        #    mc.publish_date_query( today - datetime.timedelta(180), today),
        #    "'media_id:{}'".format(COLLECTIONS[c]) ],
        #                        rows= fetch_size)
        ##
        # above query fails, below query works.
        ##
        wm = mc.storyWordMatrix('({})'.format(t),
                                '+publish_date:[{}T00:00:00Z TO {}T00:00:00Z] AND +tags_id_media:{}'.format(today - datetime.timedelta(180), today, COLLECTIONS[c]),
                                rows= fetch_size)
        this_query['stories'] = [mc.story(x) for x in wm['word_matrix'].keys()]
        this_query["word_list"] = wm['word_list']
        this_query['word_matrix'] = wm['word_matrix']
        result_list.append(this_query)
 with open('wm_json.txt', 'wb') as wmr:
    wmr.write(json.dumps(result_lis, default=str).encode())

