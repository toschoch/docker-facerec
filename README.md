Docker Face Recognition WebService
===============================
author: Tobias Schoch

Overview
--------

A small web service running in a docker container that enables face recognition in images.


Change-Log
----------
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

REST-API:

faces
image/indentify
image/teach
facecode/identify
facecode/teach
