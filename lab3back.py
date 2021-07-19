#Name: Christopher Bryan
#Purpose: Lab 3 - Back-end

import requests
from bs4 import BeautifulSoup 
import re
import collections
import json
import sqlite3

'''PART A'''
movieDict = collections.defaultdict(list)

page = requests.get('https://editorial.rottentomatoes.com/article/most-anticipated-movies-of-2021/')
soup = BeautifulSoup(page.content, 'lxml')

info = soup.find(id='article_main_body')

movies = info.select('p')[5: -10]
name = None

for count, elem in enumerate(movies, 1):
    names = elem.find_all(re.compile('strong|\\bb\\b', re.I))
    if names:
        for val, item in enumerate(names, 1):
            if val == 1:
                name = item.find('a')
                if name:
                    if name.text in movieDict: break
                    movieDict[name.text].append(name['href'])
                else:
                    name = item
                    if name.text in movieDict: break
                    movieDict[name.text].append('')
            else:
                if len(names) == 3 and val in (2, 3):
                    if val == 2:
                        movieDict[name.text].append(item.previous_sibling.previous_sibling.previous_sibling.replace("\xa0", " ").strip())
                        movieDict[name.text].append(item.next_sibling.replace("\xa0", " ").strip().split(", "))
                    else:
                        movieDict[name.text].append(item.next_sibling.strip().split()[0])
                elif val == 2:
                    movieDict[name.text].append(item.next_sibling.replace("\xa0", " ").strip())
                elif val == 3:
                    movieDict[name.text].append(item.next_sibling.replace("\xa0", " ").strip().split(", "))
                else:
                    movieDict[name.text].append(item.next_sibling.strip().split()[0])

maxi = max([len(item[1][2])for item in movieDict.items()])
movieDict["Largest"].append(maxi)

'''Creating a json file'''

with open("movies.json", 'w') as outFile:
    json.dump(movieDict, outFile, indent=3)

'''PART B'''

with open("movies.json", 'r') as inFile:
    movieDict = json.load(inFile)

maximum = movieDict["Largest"][0]
movieDict.pop("Largest")

conn = sqlite3.connect("movies.db")

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS Months")
cur.execute('''CREATE TABLE Months(
                        id INTEGER NOT NULL PRIMARY KEY,
                        month TEXT UNIQUE ON CONFLICT IGNORE)''')
cur.execute("DROP TABLE IF EXISTS Movies")
cur.execute('''CREATE TABLE Movies(
                        name TEXT NOT NULL PRIMARY KEY,
                        url TEXT,
                        month INTEGER,
                        director TEXT)''')
for i in range(maximum):
    cur.execute(f'''ALTER TABLE Movies ADD COLUMN {'actor' + str(i)} TEXT''')

for name, val in movieDict.items():
    cur.execute("INSERT INTO Months (month) VALUES (?)", (val[-1],))
    cur.execute("SELECT id FROM Months WHERE month=?", (val[-1],))
    month_id = cur.fetchone()[0]
    cur.execute("INSERT INTO Movies (name, url, month, director) VALUES (?, ?, ?, ?)", (name, val[0], month_id, val[1]))
    for count, actor in enumerate(val[2]):
        cur.execute(f"UPDATE Movies SET actor{str(count)}=? WHERE name=?", (actor, name))

conn.commit()
conn.close()
