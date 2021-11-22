FROM python:3.7-alpine
#FROM python:3.8.3-alpine

#RUN mkdir /app

#WORKDIR /app

COPY . /

RUN pip install --upgrade pip & pip install opencv-python numpy scipy
# && pip install opencv-contrib-python==4.5.4.58 
RUN apk add --no-cache --virtual .build-deps gcc musl-dev jpeg-dev zlib-dev && pip install Pillow
#python3-dev  

RUN python -m pip install -r requirements.txt --no-cache-dir

RUN adduser -D dockuser
RUN chown dockuser:dockuser -R /
USER dockuser

CMD ["python", "server.py"]
