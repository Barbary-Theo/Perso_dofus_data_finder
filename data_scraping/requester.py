import logging
import math
import requests
import random
import time

from database_connector import DatabaseConnector
from type import Type
from html_parser import HTMLParser
from text_parser import TextParser


class Requester:
    DOFUS_URL_ARCHIVE = {"resource": "https://www.dofus.com/fr/mmorpg/encyclopedie/ressources?sort=1A&",
                         "consommable": "https://www.dofus.com/fr/mmorpg/encyclopedie/consommables?sort=1A&",
                         "apparat": "https://www.dofus.com/fr/mmorpg/encyclopedie/objets-d-apparat?sort=1A&"}
    DOFUS_URL_ARCHIVE_NB_ELE_PER_PAGE = 24
    DOFUS_TOTAL_CONTENT_TAG_TARGET = "div"
    DOFUS_TOTAL_CONTENT_CLASSES_TARGET = ["ak-list-info"]
    DOFUS_TOTAL_CONTENT_DUMB_TEXT = "éléments correspondent à vos critères"
    DOFUS_CONTENT_TAG_TARGET = "tr"
    DOFUS_CONTENT_CLASSES_TARGET = ["ak-bg-odd", "ak-bg-even"]

    DATABASE_CONNECTOR = DatabaseConnector()

    def __init__(self):
        logging.info("- Requester started -")

    def get_total_content(self, type):
        response_content = self.request_dofus_by_page_and_type(1, type)
        if response_content.__contains__("Failed"):
            return -1

        html_parser = HTMLParser(
            {"tag": self.DOFUS_TOTAL_CONTENT_TAG_TARGET, "classes": self.DOFUS_TOTAL_CONTENT_CLASSES_TARGET})
        html_parser.feed(response_content)
        total_content = html_parser.all_target_tag_content

        try:
            for content in total_content:
                content_parsed = content.replace(self.DOFUS_TOTAL_CONTENT_DUMB_TEXT, "")
                if content_parsed != "":
                    return int(content_parsed)
        except Exception as ignored:
            return -1

        return -1

    def request_dofus_by_page_and_type(self, page, type):
        response = requests.get(self.DOFUS_URL_ARCHIVE[type.value] + f"page={page}")
        return response.text if response.status_code == 200 else f"Failed to fetch URL with page{page}"

    def get_data_on_page(self, page, type):
        response_content = self.request_dofus_by_page_and_type(page, type)
        if response_content.__contains__("Failed"):
            return [], response_content

        html_parser = HTMLParser(
            {"tag": self.DOFUS_CONTENT_TAG_TARGET, "classes": self.DOFUS_CONTENT_CLASSES_TARGET})
        html_parser.feed(response_content)
        type_content = html_parser.all_target_tag_content

        objects = []
        for content in type_content:
            text_parser = TextParser(content)
            object = text_parser.get_object(type)
            if object is not None:
                objects.append(object)

        return objects, "Successfully collected"

    def update_dofus_by_type(self, type: Type = Type.RESOURCE):
        total_objects = self.get_total_content(type)
        if total_objects == -1:
            return [], f"Impossible to get total {type}"
        total_page = math.ceil(total_objects / self.DOFUS_URL_ARCHIVE_NB_ELE_PER_PAGE)

        all_objects = []
        for page in range(1, total_page + 1):
            print(f" -> reading page {page}/{total_page}")
            objects, status = self.get_data_on_page(page, type)
            if not objects or not status.__contains__("Successfully"):
                return [], f"Failed to get {type}"
            self.DATABASE_CONNECTOR.insert_list_of_data_into_item(objects)
            all_objects.extend(objects)
            random_sleep_time = random.uniform(5, 10)
            print(f"Sleeping for {int(random_sleep_time)} seconds before next call to cancel status 1015\n")
            time.sleep(random_sleep_time)

        return all_objects, "Successfully updated"

    def update_dofus(self):
        resources, resources_status = self.update_dofus_by_type(Type.RESOURCE)
        consommables, consommables_status = self.update_dofus_by_type(Type.CONSOMMABLE)
        apparats, apparats_status = self.update_dofus_by_type(Type.APPARAT)

        return consommables, resources, apparats, "Successfully updated"
