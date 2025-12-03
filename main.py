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
        self.flags ={} 
        for match in self.raw_flag_matches:
            self.flags[match[0]] = match[1]


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
            json.dump(data, f, indent=4, separators=(',',':'))

    def remove_command(self, name : str):
        try:
            with open("ffmpeg_cmd_list.json", "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

        data.pop(name)

        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()
        user_input_layout = QGridLayout()

        cmd_list = CmdListWidget()
        cmd_list_layout.addWidget(cmd_list)

        text_box = QTextEdit()
        text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        text_box.setFixedHeight(30)

        add_cmd = AddCmdButton()

        input_button = QPushButton()
        input_button.setText("Input")
        input_button.setFixedSize(100, 30)

        output_button = QPushButton()
        output_button.setText("Output")
        output_button.setFixedSize(100, 30)

        run_button = QPushButton()
        run_button.setText("Run")
        run_button.setFixedSize(100, 30)


        user_input_layout.addWidget(text_box,1,0)
        user_input_layout.addWidget(add_cmd,0,1)
        user_input_layout.addWidget(input_button,2,0)
        user_input_layout.addWidget(output_button,2,1)
        user_input_layout.addWidget(run_button,3,0)

        cmd_list_layout.setStretch(0, 1)
        main_layout.addLayout(cmd_list_layout)
        main_layout.addLayout(user_input_layout)
        main_layout.setStretch(0,1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.show()


class CmdListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        processor = JsonProcessor()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # i need a way to convert cmds to json and json to cmds
        for command in processor.get_all_commands():
            item = QListWidgetItem(command)
            self.addItem(item)

        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : gray;")
        self.setVerticalScrollBar(scroll_bar)

        self.itemClicked.connect(self.cmd_clicked)
    
    def cmd_clicked(self, item : QListWidgetItem):
        print (item.text())

class AddCmdButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.geometry = QRect(20,20,10,10)
    
 


app = QApplication(sys.argv)

window = MainWindow()

app.exec()