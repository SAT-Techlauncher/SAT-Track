This is the setup procedure for the GP-20U7 GPS module.

Datasheet: https://cdn.sparkfun.com/datasheets/GPS/GP-20U7.pdf

Raspberry Pi Pin connections:
  To be plugged in order:
    <Cable_Colour>-<Title>-<Raspi_Pin>
    Black-Ground-9
    White-Serial-10
    Red-VCC(3.3v)-1
    
RaspberryPi config from desktop:
  Raspberry Pi Configuration->Interfaces Tab->Serial Port = Enable
  Raspberry Pi Configuration->Interfaces Tab->Serial Console = Enable
  
Restart RaspberryPi

run:
  sudo cat /dev/ttyS0
  
This should print out comma separated values from the device. e.g:

  $GPVTG,,,,,,,,,N*30
  $GPGGA,043149.00,,,,,0,00,99.99,,,,,,*6D
  $GPGSA,A,1,,,,,,,,,,,,,99.99,99.99,99.99*30
  $GPGSV,1,1,01,03,,,19*73
  $GPGLL,,,,,043149.00,V,N*41
  $GPRMC,043150.00,V,,,,,,,110520,,,N*7C

This verifies that the device is functioning. It still requires a decent lock to multiple GPS satellites to function correctly.
It is best to position the device near a window if possible.
