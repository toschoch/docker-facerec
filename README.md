Docker Face Recognition WebService
===============================
author: Tobias Schoch

Overview
--------

A small web service running in a docker container that enables face recognition in images.


Change-Log
----------
##### 0.1.1
* changed to python-facerec v0.1.0
* fixed config persistency
* added usage documentation
* exposed configuration /config/ (threshold parameter)
* changelog adapted

##### 0.1.0
* added delete and patch faces and general RESTfulness
* fixed tests

##### 0.0.2
* show number of stored faces at startup
* persistent data base configuration
* added tests for flask service
* working docker file for facerec server
* add working python-facerec
* added the service api for code and image requests
* added docker frame and package
* rerouted and nice rectangle and fontsize
* added image scaling and font size
* improved form, added routes
* basic teach and identify over web
* some small changes
* working upload
* adapted identify page
* added data directory
* update readme
* initial service draft

##### 0.0.1
* initial version


Installation
------------

#### Docker-Container
```
docker run -v data:/data -p 8081:80  --name facerec-server shocki/facerec
```
Faces database is stored in /data. The web services are exposed on port 80.

#### Local Server
To install use pip:

    git clone https://github.com/toschoch/docker-facerec.git
    pip install -r docker-facerec/requirement.txt
    python facerec_service.py

Usage
-----

Webinterface with browser on port 80.

REST-API Endpoints:

* `/faces` (GET) list of faces
* `/faces/<id or name>` (GET, PATCH, DELETE) get, modify or delete face entry
* `/config` (GET, PATCH) get or modify configuration parameters
* `/image/indentify` (POST) post an image and identify persons on it
* `/image/teach` (POST) post an image and a name to teach the system a face
* `/facecode/identify` (POST) post a facecode and identify persons on it
* `/facecode/teach` (POST) post a facecode and a name to teach the system a face

Web-API Endpoints:
* `/`, `/identify` browser interface for identification
* `/teach` browser interface for teaching
