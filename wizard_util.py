
import re
import json
from PyQt6.QtCore import QEvent


CmdChangedEventType = QEvent.registerEventType()

class CmdChangedEvent(QEvent):
    def __init__(self, data):
        super().__init__(CmdChangedEventType)
        try:
            self.cmd_key, self.cmd_input = next(iter(data.items()))
        except StopIteration:
            raise ValueError("CmdChangedEvent received empty dict")



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

    def get_command(self, name : str) -> dict:
        return self.get_all_commands()[name]
    
    def add_command(self, name : str, cmd : str):
        parser = CmdParser(cmd)
        try:
            data = self.get_all_commands()
        except json.JSONDecodeError:
            data = {}
        
        data[name] = parser.flags

        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))

    def remove_command(self, name : str):
        try:
            data = self.get_all_commands()
        except json.JSONDecodeError:
            data = {}

        data.pop(name)

        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


