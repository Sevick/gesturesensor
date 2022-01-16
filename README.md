# Gesture sensor

PAJ7620U2 external homeassistant sensor

Don't forget to set HASSURL and HASSTOKEN

On gesture recognition will fire events:

- EVENTNAME: action = up
- EVENTNAME: action = down
- EVENTNAME: action = left
- EVENTNAME: action = right
- EVENTNAME: action = forward
- EVENTNAME: action = backward
- EVENTNAME: action = clockwise
- EVENTNAME: action = counterclockwise
- EVENTNAME: action = wave

Default EVENTNAME is "pi4gesture" and can be redifined via GESTURE_EVENTNAME enviroment variable.
Delay between measurements can be set using LINUXMON_DELAY (by default - 0.05)