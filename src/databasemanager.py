from loggerwrapper import Logger
from couchdb import *
import pandas as pd
import numpy as np
import json, re
import os
import uuid

DIR_NAME = os.path.dirname(__file__)

class DatabaseManager():

    __logger = None
    __process_name = "Database Manager"
    __couchdb_server = None 

    def __init__(self, username, password, address, logger=None):
        self.__configure_logger(logger)
        self.couchdb_server = self.initialize_couchdb_server(username, password, address)

    def __configure_logger(self, logger=None):
        try:
            if logger != None:
                self.__logger = logger
            else:
                self.__logger = Logger("Database Manager")
        except Exception as e:
            print("{process_name}.configure_logger(): Couldn't configure a logger because: {e}".format(process_name=self.__process_name, e=e))
            raise

    def get_couchdb_server(self):
        return self.__couchdb_server

    def initialize_couchdb_server(self, username, password, address="http://127.0.0.1:5984"):
        try:
            secure_loging_string= "://{username}:{password}@".format(username=username, password=password)
            secure_login_address = re.sub(r""":\/\/""", secure_loging_string, address)
            self.__logger.debug("{process_name}.initialize_couchdb_server(): Accessing server {a} with username {u}".format(process_name=self.__process_name, a=address, u=username))
            server = Server(secure_login_address)
            server.resource.session.disable_ssl_verification()
            
        except Exception as e:
            self.__logger.error("{process_name}.initialize_couchdb_server(): Couldn't connect to server {name} because: {e}".format(process_name=self.__process_name, name=address, e=e))
            raise
        return server

    def create_couchdb_database(self, database_name):
        try:
            database = self.couchdb_server.create(database_name)
        except Exception as e:
            self.__logger.error("{process_name}.create_couchdb_database(): Couldn't create database {name} because: {e}".format(process_name=self.__process_name,
                name=database_name, e=e))
            raise

    def delete_couchdb_database(self, database_name):
        try:
            self.couchdb_server.delete(database_name)
        except Exception as e:
            self.__logger.error("{process_name}.create_couchdb_database(): Couldn't delete database {name} because: {e}".format(process_name=self.__process_name,
                name=database_name, e=e))
            raise

    def __add_element_to_database(self, database_name, element):
        try:
            self.couchdb_server[database_name].save(element)
        except Exception as e:
            self.__logger.error("{process_name}.create_couchdb_database(): Couldn't add element to database {db_name} because: {e}".format(process_name=self.__process_name, db_name=database_name))
            raise

    def populate_database_from_csv(self, path, database_name):
        try:
            self.__logger.debug("{process_name}.populate_database_from_csv():Loading csv file {path} as dataframe".format(process_name=self.__process_name, path= os.path.normpath(path)))
            dataframe =  pd.read_csv(path, header=[0,1])
            parsed_json = self.__from_dataframe_to_json(dataframe)
            self.__logger.debug(json.dumps(parsed_json, indent=4, sort_keys=True))
            
            for row in parsed_json["data"]:
                refactored_row_json = {}
                self.__logger.debug("{process_name}.populate_database_from_csv():Processing row".format(process_name=self.__process_name))
                refactored_row_json = self.__build_indicator_dict(row)
                self.__logger.debug(json.dumps(refactored_row_json, indent=4, sort_keys=True))
                refactored_row_json = self.__build_entry_dict_and_update_row(refactored_row_json)
                refactored_row_json = self.__build_impact_dict(refactored_row_json)
                refactored_row_json = self.__build_geography_dict(refactored_row_json)

                self.__logger.debug(json.dumps(refactored_row_json, indent=4, sort_keys=True))
                self.__add_element_to_database(database_name, refactored_row_json)

        except Exception as e:
            self.__logger.error("{process_name}.load_csv_as_dataframe(): Couldn't populate database because: {e}".format(process_name=self.__process_name, e=e))
            raise

    def __from_dataframe_to_json(self, dataframe):
        try:
            self.__logger.debug("{process_name}.__from_dataframe_to_json(): Dataframe to Json".format(process_name=self.__process_name))

            for i, columns_old in enumerate(dataframe.columns.levels):
                columns_new = np.where(columns_old.str.contains('Unnamed'), '', columns_old)
                dataframe.rename(columns=dict(zip(columns_old, columns_new)), level=i, inplace=True)
            dataframe.columns = [ ":".join(column) for column in dataframe.columns.to_flat_index()]
            dataframe.columns = dataframe.columns.str.strip(':')
            dataframe_as_json = dataframe.to_json(orient="table")
            parsed_json = json.loads(dataframe_as_json)

            return parsed_json
        except Exception as e:
            self.__logger.error("{process_name}.__from_dataframe_to_json(): couldn't transform dataframe to JSON because because: {e}".format(process_name=self.__process_name, e=e.message))
            raise


    def __build_indicator_dict(self, row):
        try:
            non_indicator_fields = ["index", "Data source", "Ecoinvent process OR other names", "Unit", "Reference quantity", ""]
            indicators = []
            refactored_row = {}
            for key, value in row.items():
                if key not in non_indicator_fields:
                    self.__logger.debug("{process_name}.__build_indicator_dict(): Processing indicator key {key}".format(process_name=self.__process_name, key=key))
                    indicator_fields = key.split(":")
                    indicator = {}
                    indicator["id"] = uuid.uuid1().int
                    indicator["method"] = indicator_fields[0]
                    indicator["category"] = indicator_fields[1]
                    indicator["indicator"] = indicator_fields[2]
                    indicator["units"] = indicator_fields[3]
                    indicator["value"] = value if value != None else 0.0
                    indicators.append(indicator)
                    refactored_row["indicators"] = indicators
                else:
                    self.__logger.debug("{process_name}.__build_indicator_dict(): Processing non indicator key {key}".format(process_name=self.__process_name, key=key))
                    refactored_row[key] = value
                    self.__logger.debug(json.dumps(refactored_row, indent=4, sort_keys=True))


            return refactored_row

        except Exception as e:
            self.__logger.error("{process_name}.__build_indicator_dict(): couldn't extract indicators info because because: {e}".format(process_name=self.__process_name, e=e.message))
            raise

    def __build_entry_dict_and_update_row(self, row):
        try:
            ecoinvent_fields = row["Ecoinvent process OR other names"].split(",")
            ecoinvent_fields = [field.strip() for field in ecoinvent_fields]

            ecoinvent_contains_extra_field = len(ecoinvent_fields) > 4
            index_offset = 1 if ecoinvent_contains_extra_field else 0

            entry_dict = {}
            entry_dict["id"] = uuid.uuid1().int
            entry_dict["product_name"] = "{name_part_1} {name_part_2}".format(name_part_1=ecoinvent_fields[index_offset-1], name_part_2=ecoinvent_fields[index_offset]) if ecoinvent_contains_extra_field else ecoinvent_fields[index_offset]
            entry_dict["geography"] = ecoinvent_fields[index_offset + 1].strip("[]")
            row["method"] = ecoinvent_fields[index_offset + 2]
            entry_dict["unit"] = row["Unit"]
            row["entry"] = entry_dict
            row.pop("Ecoinvent process OR other names")

            return row
        except Exception as e:
            self.__logger.error("{process_name}.__build_entry_dict_and_update_row(): couldn't extract entry info because because: {e}".format(process_name=self.__process_name, e=e.message))
            raise

    def __build_impact_dict(self, row):
        try:
            row["impacts"] = []

            for indicator in row["indicators"]:
                impact_dict= {}
                impact_dict["id"] = uuid.uuid1().int
                impact_dict["indicator_id"] = indicator["id"]
                impact_dict["entry_id"]= row["entry"]["id"]
                impact_dict["coefficient"] = indicator["value"]#indicator["value"] if indicator["value"] != None else 0.0
                row["impacts"].append(impact_dict)

            return row
        except Exception as e:
            self.__logger.error("{process_name}.__build_impact_dict(): couldn't extract impacts info because because: {e}".format(process_name=self.__process_name, e=e.message))
            raise

    def __build_geography_dict(self, row):
        try:
            row["geography"] = {
                "id": row["entry"]["geography"],
                "name": row["entry"]["geography"],
                "short_name": row["entry"]["geography"]
            }

            return row
        except Exception as e:
            self.__logger.error("{process_name}.__build_indicator_dict(): couldn't extract geography info because because: {e}".format(
                process_name=self.__process_name, e=e.message))
            raise

