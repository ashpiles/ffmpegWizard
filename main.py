import sys
import wizard_util as util
import re
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

processor = util.processor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()
        user_input_layout = QVBoxLayout()
        user_input_upper_layout = QGridLayout()
        user_input_lower_layout = QGridLayout()

        self.cmd_list = CmdListWidget()
        cmd_list_layout.addWidget(self.cmd_list)

        text_box = QTextEdit()
        text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        text_box.setFixedHeight(30)

        self.add_cmd = AddCmdButton(text_box)

        self.input_list = CmdInputListWidget()

        output_button = IOButton(util.IOButtonEnum.NEWFILE)
        output_button.setText("Output")
        output_button.setFixedSize(100, 40)

        run_button = QPushButton()
        run_button.setText("Run")
        run_button.setFixedSize(100, 40)

        user_input_upper_layout.addWidget(text_box,1,0)
        user_input_upper_layout.addWidget(self.add_cmd,0,1)

        user_input_lower_layout.addWidget(self.input_list,0,0)
        user_input_lower_layout.addWidget(output_button,0,1)
        user_input_lower_layout.addWidget(run_button,2,0)

        cmd_list_layout.setStretch(0, 1)
        user_input_layout.addLayout(user_input_upper_layout)
        user_input_layout.addLayout(user_input_lower_layout)
        main_layout.addLayout(cmd_list_layout)
        main_layout.addLayout(user_input_layout)
        main_layout.setStretch(0,1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.show()

    def event(self, e):
        if e.type() == util.CmdChangedEventType:
            self.input_list.update_list(e.cmd_input)
            self.cmd_list.update_list()
            return True
        return super().event(e)

    
class CmdInputListWidget(QWidget):
    def __init__(self):
        super().__init__()
        global processor

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.list_layout = QVBoxLayout()
        self.container.setLayout(self.list_layout)

        self.scroll.setWidget(self.container)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll)
        self.setLayout(main_layout)

        self.label_width = 70

    def add_row(self, label_text: str, flag: str = ""):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        row_widget.setMaximumHeight(60)

        if flag == "-i":
            input_button = IOButton(util.IOButtonEnum.FILE)
            input_button.setText("Browse for Input Video")
            input_button.setMinimumWidth(self.label_width)
            input_button.setMaximumWidth(self.label_width + 100)
            input_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            row_layout.addWidget(input_button)
            self.list_layout.addWidget(row_widget)

        elif label_text != "":
            label = QLabel(label_text)
            label.setMinimumWidth(self.label_width)
            label.setMaximumWidth(self.label_width)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            editor = QLineEdit("")
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            row_layout.addWidget(label)
            row_layout.addWidget(editor)

            self.list_layout.addWidget(row_widget)
    
    # need to make it so -i flag is listed as input and opens file browser
    def update_list(self, input_list: dict):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for flag, value in input_list.items():
            value_str = str(value)

            # Match label in brackets
            label_match = re.fullmatch(r"\[(.*?)\]", value_str)
            label = label_match.group(1) if label_match else ""

            # Match filename with dot (e.g., output.mp4)
            out_match = re.search(r".*\..*", value_str)
            out_name = out_match.group(0) if out_match else ""

            self.add_row(label, flag)



class CmdListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        global processor
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # i need a way to convert cmds to json and json to cmds
        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : gray;")
        self.setVerticalScrollBar(scroll_bar)
        self.update_list()

        self.itemClicked.connect(self.cmd_clicked)
    
    def update_list(self):
        self.clear()
        for command in processor.get_all_commands():
            item = QListWidgetItem(command)
            self.addItem(item)
    
    def cmd_clicked(self, item : QListWidgetItem):
        global processor
        current_cmd = {item.text() : processor.get_command(item.text())}
        QApplication.postEvent(window, util.CmdChangedEvent(current_cmd))


class AddCmdButton(QPushButton):
    def __init__(self, input_text_box : QTextEdit):
        super().__init__()
        self.geometry = QRect(20,20,10,10)
        self.clicked.connect(self.add_new_cmd)
        self.input_box = input_text_box
    
    def add_new_cmd(self):
        processor.add_command("test", self.input_box.toPlainText())



class IOButton(QPushButton):
    def __init__(self, io_type : util.IOButtonEnum):
        super().__init__()
        self.io_type = io_type
        self.io_path = ""
        self.clicked.connect(self.get_io_func())

    def get_io_func(self):
        match self.io_type:
            case util.IOButtonEnum.FILE:
                return self.browse_for_file
            case util.IOButtonEnum.DIRECTORY:
                return self.browse_for_directory
            case util.IOButtonEnum.NEWFILE:
                return self.browse_for_save_directory
        
    def browse_for_directory(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Directory")

        if folder_path:
            self.io_path = folder_path
            return folder_path
        return ""
    
    def browse_for_save_directory(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Output File", "", "Video Files (*.mp4);;All Files (*)")

        if file_path:
            self.io_path = file_path
            return file_path
        return file_path

    def browse_for_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select a File","","All Files (*)")

        if file_path:
            self.io_path = file_path
            return file_path
        
        return ""
    

app = QApplication(sys.argv)

window = MainWindow()

app.exec()