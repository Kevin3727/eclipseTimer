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

If beeping activated (see `Run`), the programs start beeping (throgh the pc internal speaker) before the start and before the end of totality at intervals shown bellow [minute:second]:

5:00 single beep\
4:00 single beep
3:00 single beep
2:00 double beep
1:30 single beep
1:00 triple beep
0:50 single beep
0:40 single beep
0:30 triple beep
0:25 single beep
0:20 double beep
0:15 single beep
0:10 double beep
0:09 single beep
0:08 single beep
0:07 single beep
0:06 single beep
0:05 double beep
0:04 single beep
0:03 single beep
0:02 single beep
0:01 single beep
0:00 Long beep
