import feedparser

d = feedparser.parse('https://hnrss.org/frontpage')

if not d.entries:
    print("No entries found. RSS feed may be down.")
else:
    titles = [entry.title for entry in d.entries[:5]]
    with open("headlines.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(titles))
    print("✅ Saved headlines.txt:")
    print("\n".join(titles))

