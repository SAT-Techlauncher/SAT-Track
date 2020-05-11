# Setup procedure for the GP-20U7 GPS module.

Datasheet: https://cdn.sparkfun.com/datasheets/GPS/GP-20U7.pdf

## Hardware Connections
Raspberry Pi Pin connections (To be plugged in order):
Cable Colour (Type) | Raspi Pin
------------ | -------------
Black (GND) | 9
White (Serial Data) | 10
Red (VCC 3.3v) | 1
    
## Raspberry Pi Configuration
RaspberryPi config from desktop:
* Raspberry Pi Configuration->Interfaces Tab->Serial Port = Enable
* Raspberry Pi Configuration->Interfaces Tab->Serial Console = Disable
  
**Restart RaspberryPi**

run:
```
  sudo cat /dev/ttyS0
  ```
This should print out comma separated values from the device (or similar):
```
  $GPVTG,,,,,,,,,N*30
  $GPGGA,043149.00,,,,,0,00,99.99,,,,,,*6D
  $GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
  $GPGSV,1,1,01,03,,,19*73
  $GPGLL,,,,,043149.00,V,N*41
  $GPRMC,043150.00,V,,,,,,,110520,,,N*7C
```
This verifies that the device is communicating. It still requires a decent lock to multiple GPS satellites to function correctly.
It is best to position the device near a window if possible.

##The following is to be able to use python libraries with the device and to test out any other info you may need.

After getting successful queries above, enter into terminal:
```
  sudo apt-get install gpsd python-gps gpsd-clients
  ```
Edit the following file:
```
  /etc/defaults/gpsd
  ```
  To look like:
	```
    # Default settings for the gpsd init script and the hotplug wrapper.

    # Start the gpsd daemon automatically at boot time
    START_DAEMON="true"

    # Use USB hotplugging to add new USB devices automatically to the daemon
    USBAUTO="true"

    # Devices gpsd should collect to at boot time.
    # They need to be read/writeable, either by user gpsd or the group dialout.
    DEVICES="/dev/ttyS0"

    # Other options you want to pass to gpsd
    GPSD_OPTIONS=""
    ```
run in terminal (not all are neccesary):
```
  sudo apt-get install python-gi-cairo
  sudo systemctl enable gpsd.service
  sudo systemctl enable gpsd.socket
  sudo systemctl start gpsd.service
  sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock
```

Run the following in terminal to get some info back:
  For simple display:
	```
    cgps -s
		```
  For GUI:
	```
  xgps
  ```
	
==================================

This may be handy:
  https://ozzmaker.com/using-python-with-a-gps-receiver-on-a-raspberry-pi/  Useful for interfaceing with python
  http://orbitalfruit.blogspot.com/2017/04/raspberry-pi-gps.html  Not everything here is relevant and is for an older version
  https://nationpigeon.com/gps-raspberrypi/ Not everything here is relevant and is for an older version
