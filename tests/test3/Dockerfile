FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests && pip3 install bs4
ADD test3.py ./
CMD python3 test3.py alice wonderland "hello world" "Paris"; python3 test3.py alice wonderland "hello world" ""; python3 test3.py alice wonderland "hello world" "Singapour"
