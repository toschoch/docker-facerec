FROM alpine:latest

# RUN apk add --update --no-cache bash ca-certificates && update-ca-certificates
RUN apk add --update --no-cache bash ca-certificates python3 \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && update-ca-certificates \
    && rm -r /root/.cache

RUN python3 -m pip install --upgrade pip

RUN apk add --no-cache --virtual .build-deps build-base gcc abuild binutils binutils-doc gcc-doc python3-dev
RUN apk add cmake cmake-doc

RUN pip install dlib \
    && apk del .build-deps \
    && rm -r /root/.cache


# Copy web service script
ADD *.py /
ADD requirements.txt /

# Install
RUN pip3 install -r requirements.txt


# Start the web service
ENTRYPOINT ['python3','facerec_service.py']
