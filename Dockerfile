FROM alpine:latest as base

FROM base as builder
ADD requirements.txt /

# RUN apk add --update --no-cache bash ca-certificates && update-ca-certificates
RUN apk add --update --no-cache bash ca-certificates python3 \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools wheel\
    && update-ca-certificates \
    && rm -r /root/.cache

RUN python3 -m pip install --upgrade pip
RUN apk add --no-cache --virtual .build-deps \
                       build-base \
                       gcc \
                       git \
                       python3-dev \
                       cmake \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev

COPY packages/fortify-headers.h /usr/include/fortify/

RUN pip3 wheel --wheel-dir=/local/wheels --index-url=http://dietzi.ddns.net:3141/dietzi/stable --trusted-host=dietzi.ddns.net -r requirements.txt

FROM base

COPY --from=builder /local/wheels /local/wheels
ADD requirements.txt /

RUN apk add --update --no-cache bash ca-certificates python3 libstdc++ libjpeg libpng freetype\
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --no-cache --upgrade pip \
    && pip3 install --no-index --find-links=/local/wheels facerec \
    && pip3 install --no-index --find-links=/local/wheels -r requirements.txt \
    && rm -r /local/wheels

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
