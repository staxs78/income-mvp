import feedparser, pprint

d = feedparser.parse('https://hnrss.org/frontpage')
pprint.pprint([e.title for e in d.entries[:5]])
