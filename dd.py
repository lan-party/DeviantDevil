from lxml import html
import requests
import time
import random


searchlist = ["nature", "space", "wallpaper", "future", "brushes", "tattoo", "abstract", "pixel art", "dinosaur", "neon", "tshirt", "mushroom",
              "steampunk", "sticker", "scifi", "octopus", "psychedelic", "isometric", "jellyfish", "kawaii", "cyberpunk", "magic", "magick", "occult"]

# savestate.txt won't be created automatically
# To start from the beginning of the search list, the contents of savestate.txt should be "0,1"
savestate = open("savestate.txt", "r")
save = savestate.read().split(",")
searchliststate = int(save[0])
resultspagestate = int(save[1])
savestate.close()
print("Starting from SearchListState '"+str(searchliststate)+"' and ResultsPage '"+str(resultspagestate)+"'")

# Loop through search terms
for a in range(searchliststate, len(searchlist)-1):
    search = searchlist[a]
    print("Search-term:\t\t'"+search+"'")

    # Loop through pages of search results
    resultspage = resultspagestate
    resultspagestate = 1
    while True:
        print(time.ctime())
        print("Page:\t\t\t"+str(resultspage))
        page = requests.get("https://www.deviantart.com/search/deviations?order=popular-all-time&page="+str(resultspage)+"&q="+search)

        # Check for the end of search results
        if ">There was an error performing your request.<" in str(page.content):
            break

        # Create a list of post links
        pagetree = html.fromstring(page.content)
        linklist = []
        for links in pagetree.xpath('//a[@data-hook="deviation_link"]/@href'):
            if links not in linklist:
                linklist.append(links)
        print("Deviations to check:\t"+str(len(linklist)))

        # Loop through link list
        for link in linklist:
            # Request post from link
            page = requests.get(link)

            # Wait for rate limiter if the request fails
            if page.status_code != 200:
                print("Rate limit reached. Waiting 15 minutes...")
                time.sleep(15*60)
                page = requests.get(link)
                if page.status_code != 200:
                    print("Rate limiter still active. Waiting 1 hour...")
                    time.sleep(60*60)
                    page = requests.get(link)

            # Add creative commons by and by-sa licensed post links to datlog.txt
            if "creativecommons.org/licenses/by/" in page.text or "creativecommons.org/licenses/by-sa/" in page.text:
                datlog = open("datlog.txt", "r")
                if link not in datlog.read():
                    datlog.close()
                    datlog = open("datlog.txt", "a")
                    datlog.write(link+"\n")
                    datlog.close()
                else:
                    datlog.close()
                print(link)

            # 3 seconds seems to be a good pause time
            time.sleep(3)

        # Save page number
        resultspage += 1
        savestate = open("savestate.txt", "w")
        savestate.write(str(a)+","+str(resultspage))
        savestate.close()
    # Save search list location
    savestate = open("savestate.txt", "w")
    savestate.write(str(a)+",1")
    savestate.close()
