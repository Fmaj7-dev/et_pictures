#!/usr/local/bin/python

import sqlite3


class Database():
    def __init__ (self):
        self.con = None

    def connectToDatabase(self, dbName):
        self.con = sqlite3.connect(dbName)

    def dropDatabase(self):
        cur = self.con.cursor()

        # clean previous tables
        cur.execute("DROP TABLE IF EXISTS image")
        cur.execute("DROP TABLE IF EXISTS imagetag")
        cur.execute("DROP TABLE IF EXISTS tag")
        cur.execute("DROP TABLE IF EXISTS imagepermission")
        cur.execute("DROP TABLE IF EXISTS permission")

    def createDatabase(self):
        cur = self.con.cursor()

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

        self.con.commit()
    
    def insertTestData(self):
        cur = self.con.cursor()
        self.con.set_trace_callback(print)
        cur.execute("""INSERT into image (ImageName, Width, Height) values ("123456789.jpg", 800, 600);""")
        cur.execute("""INSERT into image (ImageName, Width, Height) values ("asdfqwer.jpg", 1024, 768);""")
        cur.execute("""INSERT into image (ImageName, Width, Height) values ("zxcvqer.jpg", 2048, 1536);""")


        cur.execute("""INSERT into tag (TagName) values ("family");""")
        cur.execute("""INSERT into tag (TagName) values ("country side");""")

        cur.execute("""INSERT into imagetag (ImageId, TagId) values (1, 1);""")
        cur.execute("""INSERT into imagetag (ImageId, TagId) values (2, 1);""")
        cur.execute("""INSERT into imagetag (ImageId, TagId) values (2, 2);""")
        cur.execute("""INSERT into imagetag (ImageId, TagId) values (3, 2);""")

        self.con.commit()

    def printDatabase(self):
        cur = self.con.cursor()
        res = cur.execute("select * from image, imagetag, tag where image.imageid == imagetag.imageid and imagetag.tagid == tag.tagid;")
        print(res.fetchall())

    def getImages(self):
        cur = self.con.cursor()
        res = cur.execute("select * from image;")
        return res.fetchall()

    # Given an image name, return its tags
    # Used when editing tags
    def getImageTags(self, imageName):
        cur = self.con.cursor()
        res = cur.execute("""SELECT tag.TagName FROM image, imagetag, tag 
                            WHERE image.imageid == imagetag.imageid AND 
                                imagetag.tagid == tag.tagid AND 
                                image.imageName ==\""""+imageName+"\";")
        tags = res.fetchall()
        return tags

    # tags is a set of strings
    # imageId is an integer
    def removeTagFromImage(self, imageId, tags):
        cur = self.con.cursor()

        for tag in tags:
            res = cur.execute("SELECT * FROM tag WHERE tag.tagName == \""+tag+"\";")
            l = res.fetchall()
            tagId = int(l[0][0])
            cur.execute("DELETE FROM imagetag WHERE imagetag.imageId == "+str(imageId)+" AND imagetag.tagId == "+str(tagId)+";")
        self.con.commit()

    def addTagsToImage(self, imageId, tags):
        cur = self.con.cursor()

        for tag in tags:
            # search tag
            res = cur.execute("SELECT * FROM tag WHERE tag.tagName == \""+tag+"\";")
            l = res.fetchall()

            if len(l) < 1:
                # insert tag
                cur.execute("INSERT INTO tag (tagName) VALUES (\""+tag+"\");")
                res = cur.execute("SELECT * from tag WHERE tag.tagName == \""+tag+"\";")
                l = res.fetchall()
            if len(l) > 1:
                print("error: several tags with the same name: "+tag)
                exit()

            tagId = int(l[0][0])


            # search imagetag
            res = cur.execute("SELECT * FROM imagetag WHERE imagetag.tagId == "+str(tagId)+" AND imagetag.imageId == "+str(imageId)+";")
            l = res.fetchall()
            if len(l) < 1:
                cur.execute("INSERT INTO imagetag (imageid, tagid) VALUES ("+str(imageId)+", "+str(tagId)+");")


    # When the admin updates the tags in edit mode
    # newTags is a set
    def updateImageTags(self, imageName, newTags, width, height):
        # if image does not exist, create
        cur = self.con.cursor()
        res = cur.execute("SELECT image.imageId FROM image  where image.imageName == \""+imageName+"\"")
        l = res.fetchall()

        # if image does not exist, create it and obtain the id
        if len(l) < 1:
            cur.execute("INSERT INTO image (ImageName, Width, Height) VALUES (\""+imageName+"\","+str(width)+","+str(height)+");")
            self.con.commit()
            res = cur.execute("SELECT image.imageId FROM image WHERE image.imageName == \""+imageName+"\"")
            l = res.fetchall()
        if len(l) > 1:
            print("error, several images with the same name: "+imageName)
            exit()

        imageId = int(l[0][0])

        # if there is an old tag, not in the new tags list, remove it and imagetag related
        oldTags = self.getImageTags(imageName)
        oldTags = set( [item for t in oldTags for item in t] )
        tagsToRemove = oldTags - newTags
        self.removeTagFromImage(imageId, tagsToRemove)

        # if tag does not exist, create it and create an imagetag
        tagsToAdd = newTags - oldTags
        self.addTagsToImage(imageId, tagsToAdd)

        self.con.commit()

    # When the final user browses the images
    def getImagesByTag(self, tagName):
        cur = self.con.cursor()
        res =cur.execute("""SELECT image.ImageName FROM image, imagetag, tag 
                            WHERE image.imageid == imagetag.imageid AND 
                                imagetag.tagid == tag.tagid AND 
                                tag.tagName ==\""""+tagName+"\";")

        images = res.fetchall()
        return images

def test():
    db = Database()
    db.connectToDatabase("test.db")
    db.createDatabase()
    db.insertTestData()
    db.updateImageTags("newimage.jpg", {"karma", "police"}, 320, 240)
    db.updateImageTags("newimage.jpg", {"karma", "radio"}, 320, 240)
    db.printDatabase()

