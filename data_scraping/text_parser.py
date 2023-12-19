import re
import json


class TextParser():

    def __init__(self, text):
        self.text = text

    def get_object(self, type):
        pattern_data_content = r'\{[^}]*\}'
        pattern_brackets_content = r'\{[^{}]*\}'

        try:
            data_content = re.sub(pattern_data_content, '', self.text)
            brackets_content = re.findall(pattern_brackets_content, self.text)
            data_content = data_content.split("}")

            object = {}
            object["id"] = int(json.loads(brackets_content[0])["id"])
            object["name"] = data_content[1]
            object["type"] = data_content[2].split("Niv.")[0]
            object["level"] = int(data_content[2].split("Niv.")[1].replace(" ", ""))
            object["main_type"] = type.value

            return object
        except Exception as ignored:
            return None
