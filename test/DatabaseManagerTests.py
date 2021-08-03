import pytest
from os import sys, path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from databasemanager import DatabaseManager

# def test_couchdb_is_accessible():
#     print("Test that CouchDB server can be accessed")
#     manager = DatabaseManager("admin", "admin", "http://127.0.0.1:5984/")
#     assert manager != None

# def test_create_and_delete_database():
#     manager = DatabaseManager("admin", "admin", "http://127.0.0.1:5984/")
#     database_name = "test_database"
#     print("Creating database {db}".format(db=database_name))
#     manager.create_couchdb_database(database_name)
#     database = manager.couchdb_server[database_name]
#     print("Created Database {db}".format(db=database.name))
#     print("Deleting database {db}".format(db=database_name))
#     manager.delete_couchdb_database(database_name)
#     assert not database_name in manager.couchdb_server

def test_populate_database_using_csv():    
    manager = DatabaseManager("admin", "admin", "http://127.0.0.1:5984/")
    database_name = "test"
    manager.create_couchdb_database(database_name)
    database = manager.couchdb_server[database_name]
    print("Created Database {db}".format(db=database.name))

    path=r"C:\Users\JulianRuizBurgos\Google Drive\Repositories\rivm2016_Julian\data\rivm2016.csv"
    print("Reading CSV and populating database")
    manager.populate_database_from_csv(path, database_name)
    #missing check for elements added to database
    print("Deleting database {db}".format(db=database_name))
    manager.delete_couchdb_database(database_name)
    assert not database_name in manager.couchdb_server
