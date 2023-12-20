import pymysql
from datetime import datetime


class DatabaseConnector():

    def open_connection(self):
        mydb = pymysql.connect(
            host="theobarbary.com",
            user="barbary",
            password="oParleur595",
            database="dofus_data",
            port=3306
        )
        cursor = cursor = mydb.cursor()
        return mydb, cursor

    def insert_list_of_data_into_item(self, data):
        mydb, cursor = self.open_connection()

        insert_query = "INSERT INTO item (item_id, name, category, level, main_type) VALUES (%s, %s, %s, %s, %s)"

        for item in data:
            item_values = (item['id'], item['name'], item['type'], item['level'], item['main_type'])
            try:
                cursor.execute(insert_query, item_values)
            except pymysql.err.IntegrityError:
                pass

        mydb.commit()

        cursor.close()
        mydb.close()

        print(f"\t - {len(data)} items inserted")

    def insert_new_data_synchronization_date(self):
        mydb, cursor = self.open_connection()

        insert_query = "INSERT INTO item_synchronization (starting_date) VALUES (%s)"

        cursor.execute(insert_query, datetime.now())

        mydb.commit()

        cursor.close()
        mydb.close()
