
import re
import json


class CmdParser():
    def __init__(self, command : str):
        self.raw_flag_matches = re.findall(r"(-\S+)\s+(\S+)",command) 
        self.flags = []
        if command != "":
            out_match = re.findall(r"(?:^|\s)(-\S+\s)?(\S+)(?=\s*$)", command)
            out_flag,out_value = out_match[0]
    
            for match in self.raw_flag_matches:
                self.flags.append({"flag":match[0],"input":match[1]})
            if out_flag == '':
                self.flags.append(({"flag":"","input":out_value}))
    
    def get_cmd(self):
        cmd = "ffmpeg"
        for flag in self.flags:
            cmd += " " + flag["flag"] + " " + flag["input"]
        return cmd



class JsonProcessor():
    def __init__(self):
        f = open("ffmpeg_cmd_list.json","a")
        f.close()

    def get_all_data(self):
        with open("ffmpeg_cmd_list.json", "r") as f:
            data = json.load(f)
        return data

    def get_command(self, name : str) -> dict:
        return self.get_all_data()["commands"][name]
    
    def get_flag(self, name : str) -> dict:
        return self.get_all_data()["flags"][name]
    
    def add_flag(self, name:str, flag:str, tool_tip:str = ""):
        try:
            data = self.get_all_data()
        except json.JSONDecodeError:
            data = {}
        data["flags"][name] = {"flag":flag,"tool_tip":tool_tip}
        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


    def add_command(self, name:str, cmd:str):
        parser = CmdParser(cmd)
        try:
            data = self.get_all_data()
        except json.JSONDecodeError:
            data = {}
        data["commands"][name] = parser.flags
        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


    def remove_flag(self, name : str):
        try:
            data = self.get_all_data()
        except json.JSONDecodeError:
            data = {}
        data["flags"].pop(name)
        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


    def remove_command(self, name : str):
        try:
            data = self.get_all_data()
        except json.JSONDecodeError:
            data = {}
        data["commands"].pop(name)
        with open("ffmpeg_cmd_list.json", "w") as f:
            json.dump(data, f, indent=4, separators=(',',':'))


processor = JsonProcessor()