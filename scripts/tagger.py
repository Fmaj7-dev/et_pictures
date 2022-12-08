#!/usr/local/bin/python

import sys
from PySide6 import QtCore, QtWidgets, QtGui
import hashlib
import shutil

import database

class graphicsScene(QtWidgets.QGraphicsScene):
    def __init__ (self):
        super(graphicsScene, self).__init__ ()

class textNode(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(textNode, self).__init__()
        self.parent = parent

    def keyPressEvent(self, event):
        super(textNode, self).keyPressEvent(event)
        #if intro
        if event.key() == 16777220:
            self.parent.close()


class Tagger(QtWidgets.QWidget):
    def __init__(self, image, output_dir, database_file):
        super().__init__()

        database.connectToDatabase(database_file)
        #database.createDatabase()
        self.md5sum = hashlib.md5(open(image,'rb').read()).hexdigest()

        shutil.copy(image, output_dir+'/'+self.md5sum+'.jpg')

        print("opening "+image)
        self.background = QtGui.QPixmap(image)
        self.width = self.background.size().width()
        self.height = self.background.size().height()

        self.setMaximumWidth(self.width)
        self.setMaximumHeight(self.height)
        
        # configure scene & view
        self.scene = graphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.scene.addPixmap(self.background)

        self.text = textNode(self)

        # configure layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)

        # resize
        self.view.fitInView(QtCore.QRectF(0, 0, self.width/2, self.height/2), QtCore.Qt.KeepAspectRatio)

    def close(self):
        tags_string = self.text.toPlainText()
        print(tags_string)

        image_name = str(self.md5sum)+".jpg"
        tags = {}
        tags = set(tags_string.split(","))
        database.updateImageTags(image_name, tags, self.width, self.height )
        sys.exit()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    # create Tagger with file, output dir, and database file
    myWidget = Tagger(sys.argv[1], sys.argv[2], sys.argv[3])
    myWidget.show()
    sys.exit(app.exec_())
