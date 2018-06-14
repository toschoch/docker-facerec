FROM alpine:latest

#COPY packages/*.gz /pypkg/
#COPY packages/*.whl /pypkg/
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
                       git \
                       python3-dev \
                       cmake \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev

COPY packages/fortify-headers.h /usr/include/fortify/

RUN pip3 install -e git+https://github.com/toschoch/python-facerec.git@v0.1.5#egg=facerec \
    && pip3 install -r requirements.txt \
    && apk del .build-deps \
    && rm -r /root/.cache

RUN apk add libstdc++ libjpeg libpng freetype

# Copy web service script
COPY *.py /
RUN mkdir /static/ && mkdir /static/tmp && mkdir /data
COPY templates/ /templates/
COPY templates/*.html /templates/
COPY static/bootstrap* /static/
COPY static/*.ttf /static


EXPOSE 80
VOLUME /data

# Start the web service
CMD python3 facerec_service.py
