#!/usr/local/bin/python

import sys
from PySide6 import QtCore, QtWidgets, QtGui

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
    def __init__(self, image):
        super().__init__()

        print("opening "+image)
        self.background = QtGui.QPixmap(image)
        width = self.background.size().width()
        height = self.background.size().height()

        self.setMaximumWidth(width)
        self.setMaximumHeight(height)
        
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
        self.view.fitInView(QtCore.QRectF(0, 0, width/2, height/2), QtCore.Qt.KeepAspectRatio)

    def close(self):
        print(self.text.toPlainText())
        sys.exit()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    myWidget = Tagger(sys.argv[1])
    myWidget.show()
    sys.exit(app.exec_())
