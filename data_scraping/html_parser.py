from html.parser import HTMLParser


class HTMLParser(HTMLParser):
    def __init__(self, tag_filter: dict):
        super().__init__()
        self.inside_target_div = False
        self.target_tag_content = []
        self.all_target_tag_content = []
        self.tag_filter = tag_filter
        if tag_filter is None or tag_filter["tag"] is None or tag_filter["classes"] is None:
            self.tag_filter = None

    def handle_starttag(self, tag, attrs):
        if self.tag_filter is None:
            return

        if tag == self.tag_filter["tag"]:
            class_value = dict(attrs).get("class")
            if self.tag_filter["classes"].__contains__(class_value):
                self.inside_target_div = True

    def handle_endtag(self, tag):
        if self.tag_filter is None:
            return

        if self.inside_target_div and tag == self.tag_filter["tag"]:
            self.inside_target_div = False
            self.all_target_tag_content.append(''.join(self.target_tag_content))
            self.target_tag_content = []

    def handle_data(self, data):
        if self.tag_filter is None:
            return

        if self.inside_target_div:
            self.target_tag_content.append(data.strip())