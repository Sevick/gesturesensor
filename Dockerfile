FROM python:3.8-alpine3.12
WORKDIR /home/homeassistant/gesture/

# copy the dependencies file to the working directory
#COPY requirements.txt .

#RUN apk --update add gcc build-base freetype-dev wget git sudo wiringpi python3-smbus
RUN apk --update add gcc build-base wiringpi i2c-tools

#RUN wget https://project-downloads.drogon.net/wiringpi-latest.deb
#RUN apt install ./wiringpi-latest.deb
#RUN dpkg -i wiringpi-latest.deb


#RUN pip install WiringPi


RUN pip install pyserial
RUN pip install smbus2
RUN pip install hassapi
RUN pip install python-dotenv

#RUN git clone git://git.drogon.net/wiringPi
#RUN cd wiringPi && ./build
#RUN pip install wiringpi2


# install dependencies
#RUN pip install smbus


COPY . .
CMD ["gesture_sensor.py"]
ENTRYPOINT ["python3"] 
#ENTRYPOINT ["sh", "gesture_sensor.sh"]