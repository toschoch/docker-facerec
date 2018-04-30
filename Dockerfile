FROM alpine:latest

COPY packages/python-facerec* /pypkg/
ADD requirements.txt /

# RUN apk add --update --no-cache bash ca-certificates && update-ca-certificates
RUN apk add --update --no-cache bash ca-certificates python3 \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && update-ca-certificates \
    && rm -r /root/.cache \
    && python3 -m pip install --upgrade pip \
    && apk add --no-cache --virtual .build-deps \
                       build-base \
                       gcc \
                       python3-dev \
                       cmake \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev

COPY packages/fortify-headers.h /usr/include/fortify/

RUN find pypkg/ -type f -exec pip3 install {} \; \
    && pip3 install -r requirements.txt \
    && apk del .build-deps \
    && rm -r /root/.cache \
    && rm -r /pypkg

RUN apk add libstdc++ libjpeg libpng freetype

# Copy web service script
ADD *.py /
RUN mkdir /static/ && mkdir /static/tmp && mkdir /data
ADD templates/ /templates/
COPY templates/*.html /templates/
COPY static/bootstrap* /static/
COPY static/*.ttf /static

EXPOSE 80

# Start the web service
CMD python3 facerec_service.py
