from couchdb import *
import pandas as pd
import numpy as np
import json, re
import os

DIR_NAME = os.path.dirname(__file__)


class DatabaseManager():

    couchdb_server = None 

    def __init__(self, username, password, address):
        try:
            self.couchdb_server = self.initialize_couchdb_server(username, password, address)

        except Exception as e:
            print(
                "DatabaseManager(): Couldn't initialize couchdb server connection because: {e}".format(e=e))
            raise

    def initialize_couchdb_server(self, username, password, address="http://127.0.0.1:5984"):
        try:
            secure_loging_string= "://{username}:{password}@".format(username=username, password=password)
            secure_login_address = re.sub(r""":\/\/""", secure_loging_string, address)
            print("initialize_couchdb_server():Accessing server {a} with username {u}".format(a=address, u=username))

            server = Server(secure_login_address)
            server.resource.session.disable_ssl_verification()
            
        except Exception as e:
            print("initialize_couchdb_server(): Couldn't connect to server {name} because: {e}".format(
                name=address, e=e))
            raise
        return server

    def create_couchdb_database(self, database_name):
        try:
            database = self.couchdb_server.create(database_name)
        except Exception as e:
            print("create_couchdb_database(): Couldn't create database {name} because: {e}".format(
                name=database_name, e=e))
            raise

    def delete_couchdb_database(self, database_name):
        try:
            self.couchdb_server.delete(database_name)
        except Exception as e:
            print("create_couchdb_database(): Couldn't delete database {name} because: {e}".format(
                name=database_name, e=e))
            raise

    def __add_element_to_database(self, database_name, element):
        try:
            self.couchdb_server[database_name].save(element)
        except Exception as e:
            print("create_couchdb_database(): Couldn't add element to database {db_name} because: {e}".format(db_name=database_name))
            raise

    def populate_database_from_csv(self, path, database_name):
        try:
            print("populate_database_from_csv():Loading csv file {path} as dataframe".format(path= os.path.normpath(path)))
            dataframe =  pd.read_csv(path, header=[0,1])
            for i, columns_old in enumerate(dataframe.columns.levels):
                columns_new = np.where(columns_old.str.contains('Unnamed'), '', columns_old)
                dataframe.rename(columns=dict(zip(columns_old, columns_new)), level=i, inplace=True)
            dataframe.columns = [ " ".join(column) for column in dataframe.columns.to_flat_index()]
            dataframe.columns = dataframe.columns.str.strip()
            dataframe_as_json = dataframe.to_json(orient="table")
            parsed_json = json.loads(dataframe_as_json)
            
            for entry in parsed_json["data"]:
                self.__add_element_to_database(database_name, entry)

        except Exception as e:
            print("load_csv_as_dataframe(): Couldn't load csv file as dataframe because: {e}".format(e=e.message))
            raise
