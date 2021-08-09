# Repository
1. Clone repository locally.

# Database
## Database server: CouchDB
1. If not already installed, install .NET runtime 3.5 (https://download.microsoft.com/download/7/0/3/703455ee-a747-4cc8-bd3e-98a615c3aedb/dotNetFx35setup.exe)
2. Install CouchDB server (https://couchdbneighbourhoodie.fra1.digitaloceanspaces.com/downloads/3.1.1/win/apache-couchdb-3.1.1.msi)
3. When asked during the installation, add user _admin_ with password _admin_ as a server admin. If not prompted, after installation go to http://127.0.0.1:5984/_utils/#addAdmin/couchdb@localhost and add an admin user with name "admin" and password "admin".

## Create and populate database
4. Inside the root folder of the repository, run the python script  *_<python_command> src/CreateAndPopulateDatabase.py -u admin -p admin -d rivm2016 -s "http://127.0.0.1:5984/" -i "data/rivm2016.csv"_*

# GraphQL server
## Deployment
5. Inside the root folder of the repository, run command: *docker build -t assignment .*
6. Run command: *docker container run -p 5000:5000 -p 5984:5984 assignment*
## Access GraphQL server
7. GraphQL server will be available at http://localhost:5000/graphql

## Sample query
_query{
  entries{
    unit
  }
}_
