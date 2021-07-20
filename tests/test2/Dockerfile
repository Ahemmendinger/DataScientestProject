FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests && pip3 install bs4
ADD test2.py ./
CMD python3 test2.py alice wonderland "hello world"; python3 test2.py alice wonderland2 "hello world"; python3 test2.py alice wonderland ""
