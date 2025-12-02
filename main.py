import sys
import json
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class JsonProcessor():
    def __init__(self):
        f = open("ffmpeg_cmd_list.json","a")
        f.close()

    def get_cmd_at(self, index : int):
        with open("ffmpeg_cmd_list.json", "r") as f:
            data = json.load(f)
        print(data)
        print(type(data))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ffmpeg Wizard")

        json_processor = JsonProcessor()
        json_processor.get_cmd_at(1)

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()

        cmd_list = self.CmdScrollBox()
        cmd_list_layout.addWidget(cmd_list)

        cmd_list_layout.setStretch(0, 1)
        main_layout.addLayout(cmd_list_layout)
        main_layout.setStretch(0,1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.show()

    def CreateList(processor: JsonProcessor):
        pass


    def CmdScrollBox(self):
        list_widget = QListWidget(self)
        list_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


        item1 = QListWidgetItem("Tutorialspoint")
        item2 = QListWidgetItem("BOX 1")
        item3 = QListWidgetItem("BOX 2")
        item4 = QListWidgetItem("BOX 3")
        item5 = QListWidgetItem("BOX 4")
        item6 = QListWidgetItem("BOX 5")
        item7 = QListWidgetItem("BOX 6")
        item8 = QListWidgetItem("BOX 7")
        item9 = QListWidgetItem("BOX 8")
        item10 = QListWidgetItem("BOX 9")
        # adding items to the list widget
        list_widget.addItem(item1)
        list_widget.addItem(item2)
        list_widget.addItem(item3)
        list_widget.addItem(item4)
        list_widget.addItem(item5)
        list_widget.addItem(item6)
        list_widget.addItem(item7)
        list_widget.addItem(item8)
        list_widget.addItem(item9)
        list_widget.addItem(item10)

        # scroll bar
        scroll_bar = QScrollBar(self)
        # setting style sheet to the scroll bar
        scroll_bar.setStyleSheet("background : gray;")
        # setting vertical scroll bar to it
        list_widget.setVerticalScrollBar(scroll_bar)
        return list_widget
 


app = QApplication(sys.argv)

window = MainWindow()

app.exec()