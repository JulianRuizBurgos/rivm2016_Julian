#Base image is couchDB official image
#PULL couchdb
FROM python:3
 
ENV COUCHDB_USER=admin
ENV COUCHDB_PASSWORD=admin
RUN mkdir /app
ADD . /app
WORKDIR /app
# RUN apt-get update
# RUN apt-get install python3.9
# RUN apt install -y python3-pip
RUN pip install -r requirements.txt
EXPOSE 5000
EXPOSE 5984
CMD ["python", "src/app.py"]