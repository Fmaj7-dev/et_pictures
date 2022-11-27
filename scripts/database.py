#!/usr/local/bin/python

import sqlite3

con = None

def connectToDatabase(dbName):
    global con
    con = sqlite3.connect(dbName)

def createDatabase():
    cur = con.cursor()
    #con.set_trace_callback(print)

    # clean previous tables
    cur.execute("DROP TABLE IF EXISTS image")
    cur.execute("DROP TABLE IF EXISTS imagetag")
    cur.execute("DROP TABLE IF EXISTS tag")
    cur.execute("DROP TABLE IF EXISTS imagepermission")
    cur.execute("DROP TABLE IF EXISTS permission")

    # create tables
    cur.execute("""
            CREATE TABLE IF NOT EXISTS "image"
            (
                [ImageId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                [ImageName] NVARCHAR(160)  NOT NULL,
                [Width] INTEGER  NOT NULL,
                [Height] INTEGER  NOT NULL
            );
            """) #CREATE INDEX [IFK_ImageId] ON "image" ([ImageId]);

    cur.execute("""
            CREATE TABLE IF NOT EXISTS "tag"
            (
                [TagId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                [TagName] NVARCHAR(160)  NOT NULL
            );
            """) #CREATE INDEX [IFK_TagId] ON "tag" ([TagId]);

    cur.execute("""
            CREATE TABLE IF NOT EXISTS "imagetag"
            (
                [ImageId] INTEGER NOT NULL, 
                [TagId]   INTEGER NOT NULL, 
                constraint imagetag_pk primary key (ImageId, TagId),
                FOREIGN KEY (TagId)   REFERENCES tag   (TagId)   ON DELETE NO ACTION ON UPDATE NO ACTION
            );
            """)
            # FOREIGN KEY (ImageId) REFERENCES image (ImageId) ON DELETE NO ACTION ON UPDATE NO ACTION

    cur.execute("""
            CREATE TABLE IF NOT EXISTS "permission"
            (
                [PermissionId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                [PermissionName] NVARCHAR(160)  NOT NULL
            );
            """) #CREATE INDEX [IFK_PermissionId] ON "permission" ([PermissionId]);

    cur.execute("""
            CREATE TABLE IF NOT EXISTS "imagepermission"
            (
                [ImageId] INTEGER NOT NULL, 
                [PermissionId]   INTEGER NOT NULL, 

                FOREIGN KEY ([ImageId]) REFERENCES "image" ([ImageId]) ON DELETE NO ACTION ON UPDATE NO ACTION
            );""")
            #FOREIGN KEY ([PermissionId]) REFERENCES "permission" ([PermissionId]) ON DELETE NO ACTION ON UPDATE NO ACTION,

    con.commit()
    
def insertTestData():
    cur = con.cursor()
    con.set_trace_callback(print)
    cur.execute("""INSERT into image (ImageName, Width, Height) values ("123456789.jpg", 800, 600);""")
    cur.execute("""INSERT into image (ImageName, Width, Height) values ("asdfqwer.jpg", 1024, 768);""")
    cur.execute("""INSERT into image (ImageName, Width, Height) values ("zxcvqer.jpg", 2048, 1536);""")


    cur.execute("""INSERT into tag (TagName) values ("family");""")
    cur.execute("""INSERT into tag (TagName) values ("country side");""")

    cur.execute("""INSERT into imagetag (ImageId, TagId) values (1, 1);""")
    cur.execute("""INSERT into imagetag (ImageId, TagId) values (2, 1);""")
    cur.execute("""INSERT into imagetag (ImageId, TagId) values (2, 2);""")
    cur.execute("""INSERT into imagetag (ImageId, TagId) values (3, 2);""")

    con.commit()

def printDatabase():
    cur = con.cursor()
    res = cur.execute("select * from image, imagetag, tag where image.imageid == imagetag.imageid and imagetag.tagid == tag.tagid;")
    print(res.fetchall())

# Given an image name, return its tags
# Used when editing tags
def getImageTags(imageName):
    cur = con.cursor()
    res = cur.execute("""SELECT tag.TagName from image, imagetag, tag 
                         WHERE image.imageid == imagetag.imageid AND 
                             imagetag.tagid == tag.tagid AND 
                             image.imageName ==\""""+imageName+"\";")
    tags = res.fetchall()
    return tags

# tags is a set of strings
# imageId is an integer
def removeTagFromImage(imageId, tags):
    cur = con.cursor()

    for tag in tags:
        print("#### removing tag: "+tag)
        res = cur.execute("select * from tag where tag.tagName == \""+tag+"\";")
        l = res.fetchall()
        tagId = int(l[0][0])
        cur.execute("delete from imagetag where imagetag.imageId == "+str(imageId)+" and imagetag.tagId == "+str(tagId)+";")
    con.commit()

def addTagsToImage(imageId, tags):
    cur = con.cursor()

    for tag in tags:
        print ("#### adding tag: "+tag)
        # search tag
        res = cur.execute("select * from tag where tag.tagName == \""+tag+"\";")
        l = res.fetchall()

        if len(l) < 1:
            # insert tag
            cur.execute("insert into tag (tagName) values (\""+tag+"\");")
            res = cur.execute("select * from tag where tag.tagName == \""+tag+"\";")
            l = res.fetchall()
        if len(l) > 1:
            print("error: several tags with the same name: "+tag)
            exit()

        tagId = int(l[0][0])


        # search imagetag
        res = cur.execute("select * from imagetag where imagetag.tagId == "+str(tagId)+" and imagetag.imageId == "+str(imageId)+";")
        l = res.fetchall()
        if len(l) < 1:
            cur.execute("insert into imagetag (imageid, tagid) values ("+str(imageId)+", "+str(tagId)+");")


# When the admin updates the tags in edit mode
# newTags is a set
def updateImageTags(imageName, newTags, width, height):
    # if image does not exist, create
    cur = con.cursor()
    res = cur.execute("select image.imageId from image  where image.imageName == \""+imageName+"\"")
    l = res.fetchall()

    # if image does not exist, create it and obtain the id
    if len(l) < 1:
        cur.execute("INSERT into image (ImageName, Width, Height) values (\""+imageName+"\","+str(width)+","+str(height)+");")
        con.commit()
        res = cur.execute("select image.imageId from image  where image.imageName == \""+imageName+"\"")
        l = res.fetchall()
    if len(l) > 1:
        print("error, several images with the same name: "+imageName)
        exit()

    imageId = int(l[0][0])

    # if there is an old tag, not in the new tags list, remove it and imagetag related
    oldTags = getImageTags(imageName)
    oldTags = set( [item for t in oldTags for item in t] )
    tagsToRemove = oldTags - newTags
    removeTagFromImage(imageId, tagsToRemove)

    # if tag does not exist, create it and create an imagetag
    tagsToAdd = newTags - oldTags
    addTagsToImage(imageId, tagsToAdd)

    con.commit()

# When the final user browses the images
def getImagesByTag(tagName):
    cur = con.cursor()
    res =cur.execute("""SELECT image.ImageName FROM image, imagetag, tag 
                        WHERE image.imageid == imagetag.imageid AND 
                            imagetag.tagid == tag.tagid AND 
                            tag.tagName ==\""""+tagName+"\";")

    images = res.fetchall()
    return images

connectToDatabase("test.db")
createDatabase()
insertTestData()
updateImageTags("newimage.jpg", {"karma", "police"}, 320, 240)
updateImageTags("newimage.jpg", {"karma", "radio"}, 320, 240)
printDatabase()

