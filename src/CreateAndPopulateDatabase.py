from databasemanager import DatabaseManager
from loggerwrapper import Logger
import argparse, json, urllib3
import json

urllib3.disable_warnings()

logger = Logger("Database Manager")
config = None
process_name = "Create And Populate Database"

def run():
    try:
        logger.info("{process_name}.run(): Connecting to Database server {server} with user {user}".format(process_name=process_name, server=config["server_address"], user=config["username"]))
        
        database_manager = DatabaseManager(config["username"], config["password"], config["server_address"], logger=logger)
        
        logger.info("{process_name}.run(): Connected to Database server {server} with user {user}".format(process_name=process_name, server=config["server_address"], user=config["username"]))
        logger.info("{process_name}.run(): Accessing Database {db}".format(process_name=process_name, db=config["database_name"]))
        
        if config["database_name"] not in database_manager.couchdb_server:
            logger.info("{process_name}.run(): Database {db} doesn't exist. Creating it...".format(process_name=process_name, db=config["database_name"]))
            database_manager.create_couchdb_database(config["database_name"])
            logger.info("{process_name}.run(): Database {db} created.".format(process_name=process_name, db=config["database_name"]))
        
        logger.info("{process_name}.run(): Populating Database {db} via file {input}.".format(process_name=process_name, db=config["database_name"], input=config["input_file_path"]))
        
        database_manager.populate_database_from_csv(config["input_file_path"], config["database_name"])
        
        logger.info("{process_name}.run(): Pouplated Database {db} successfully".format(process_name=process_name, db=config["database_name"]))
    except Exception as e:
        logger.error("{process_name}.run(): Encountered an error due to {e}".format(process_name=process_name, e=e))
        raise

if __name__ == '__main__':
    # To authorize you will need to enter your username and pw
    # You can either hardcore it or fill it in the prompt

    argParser = argparse.ArgumentParser()
    argParser.add_argument('-u','--username', help='Username used for the authentication credentials', required=True)
    argParser.add_argument('-p','--password', help='Password used for the authentication credentials', required=True)
    argParser.add_argument('-s','--server_address', help='The address of the database server', required=True)
    argParser.add_argument('-d','--database_name', help='The name of the database to create/connect to. Only lowercase names are allowed.', required=True)
    argParser.add_argument('-i','--input_file_path', help='The path to the CSV file to populate the database', required=True)


    ## new parameter "only unused dashboards mode"

    passedArgs = vars(argParser.parse_args())
     
    config = {
        "username": passedArgs["username"],
        "password": passedArgs["password"],
        "server_address": passedArgs["server_address"],
        "database_name": passedArgs["database_name"],
        "input_file_path": passedArgs["input_file_path"]
    }

    logger.info("{process_name}.run(): Starting execution".format(process_name=process_name))   
    logger.debug(json.dumps(config, indent=4, sort_keys=True))
    
    run()
    
    logger.info("{process_name}.run(): Execution ended".format(process_name=process_name))   
