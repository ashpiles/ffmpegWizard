import sys
import json
import re
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class CmdParser():
    def __init__(self, command : str):
        # some commands reuse values and some require the input & outpust spots
        self.raw_flag_matches = re.findall(r"(-\S+)\s+(\S+)",command)
        self.flags = []
        for match in self.raw_flag_matches:
            self.flags.append({match[0] : match[1]})



class JsonProcessor():
    def __init__(self):
        f = open("ffmpeg_cmd_list.json","a")
        f.close()

    def get_all_commands(self) -> dict:
        with open("ffmpeg_cmd_list.json", "r") as f:
            data = json.load(f)
        return data
    
    def add_command(self, name : str, cmd : str):
        parser = CmdParser(cmd)
        try:
            with open("ffmpeg_cmd_list.json", "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
        
        data[name] = parser.flags

        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4)

        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ffmpeg Wizard")

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()

        cmd_list = CmdListWidget()
        cmd_list_layout.addWidget(cmd_list)

        cmd_list_layout.setStretch(0, 1)
        main_layout.addLayout(cmd_list_layout)
        main_layout.setStretch(0,1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.show()

class CmdListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        processor = JsonProcessor()
        processor.add_command("test_cmd", "ffmpeg -i in0.mp4 -i in1.mp4 -c copy -map 0:0 -map 1:1 -shortest out.mp4")

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # i need a way to convert cmds to json and json to cmds
        for command in processor.get_all_commands():
            self.addItem(QListWidgetItem(command))

        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : gray;")
        self.setVerticalScrollBar(scroll_bar)
 


app = QApplication(sys.argv)

window = MainWindow()

app.exec()