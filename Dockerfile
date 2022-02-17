FROM ubuntu:20.04

# Creation of app directory and copy source code inside
WORKDIR /app
COPY ./test.py .

# python3.9 installation
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9

# pip installation
RUN apt install -y python3-pip
# install python libraries
RUN python3.9 -m pip install numpy

# Expose port for chargepoints to connect to
EXPOSE 9000

CMD ["python3.9", "main.py"]