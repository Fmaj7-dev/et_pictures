#!/usr/local/bin/python

import sqlite3
con = sqlite3.connect("tutorial.db")

cur = con.cursor()
cur.execute("CREATE TABLE image(filename)")
cur.execute("CREATE TABLE imagetag(filename_id, tag_id)")
cur.execute("CREATE TABLE tag(tag)")