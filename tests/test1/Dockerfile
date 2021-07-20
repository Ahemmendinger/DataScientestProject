FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests
ADD test1.py ./
CMD python3 test1.py alice wonderland ; python3 test1.py bob builder ; python3 test1.py clementine mandarine
