# eclipseTimer
Aug 21, 2017 total solar eclipse timer

creator: Kevin Ghorbani

This timer beeps (through system sound not from the speakers) near the 2nd and 3rd connections (if there is totality at your location). It allows you to concentrate on your tasks during totlality without havinf to look at the time.

Compatible with Linux only! (python3 is needed)

Internect connection is needed for gathering the eclipse information of your location (US city/town or by entering latitude and longitude). You may save the information so you won't need internet connection at the day of the eclipse.

Remember to sync your computer clock for accuracy. Time zone does not affect the coutdown since all times are in UTC. However the local time shown is based on your computer timezone.

### Run

[optional] to activate pc speaker (beeps only if there is totality at your location):
$ sudo modprobe pcspkr

to run the program:
$ ./eclipseTimer.py

### Beeping time
