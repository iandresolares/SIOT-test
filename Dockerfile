FROM ubuntu:20.04

# Creation of app directory and copy source code inside
WORKDIR /app
COPY ./test.py /app

# python3.9 installation
RUN apt update
# pip installation
RUN apt install -y python3-pip
# install python libraries
RUN python3 -m pip install numpy
RUN python3 -m pip install numpy
# Expose port for chargepoints to connect to

CMD ["python3.9", "main.py"]