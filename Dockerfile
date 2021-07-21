FROM ubuntu:latest
ADD files ./files
ADD models ./models
ADD app.py model_builder.py ./
RUN set -xe && apt-get update && apt-get install python3-pip -y &&  pip install --upgrade pip && ls && pip install -r files/requirements.txt
CMD python3 app.py
EXPOSE 8500
