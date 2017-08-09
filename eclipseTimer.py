#!/usr/bin/env python3

import curses
import os
import pickle
import subprocess
import sys
import time
import urllib3
from datetime import datetime
from datetime import timedelta
from dateutil import tz

# Getting Location online or from file
GetLocation = True

# All times are in UTC
t0 = datetime.utcnow()
# default times are for tests only
C1 = t0.replace(hour=0, minute=0, second=7, microsecond=200000)
C2 = t0.replace(hour=0, minute=0, second=51, microsecond=400000)
C3 = t0.replace(hour=0, minute=25, second=0, microsecond=500000)
C4 = t0.replace(hour=23, minute=59, second=25, microsecond=600000)

if C1 > C2:
    raise ValueError  # C1 must be earlier than C2
if C2 > C3:
    raise ValueError  # C2 must be earlier than C3
if C3 > C4:
    raise ValueError  # C3 must be earlier than C4


Altitude = ['', '', '', '']
Azimuth = ['', '', '', '']


# Beep times
# b5:00, b4:00, b3:00, bb2:00, b1:30, bbb1:00, b0:50,  b0:40,  bbb0:30,
# b0:25, bb0:20, b0:15, bb0:10, b0:09, b0:08, b0:07, b0:06, bb0:05,
# b0:04, b0:03, b0:02, b0:01, Lb0:00
beepTimes = [[timedelta(minutes=5, seconds=0), 'b'],
             [timedelta(minutes=4, seconds=0), 'b'],
             [timedelta(minutes=3, seconds=0), 'b'],
             [timedelta(minutes=2, seconds=0), 'bb'],
             [timedelta(minutes=1, seconds=30), 'b'],
             [timedelta(minutes=1, seconds=0), 'bbb'],
             [timedelta(seconds=50), 'b'],
             [timedelta(seconds=40), 'b'],
             [timedelta(seconds=30), 'bbb'],
             [timedelta(seconds=25), 'b'],
             [timedelta(seconds=20), 'bb'],
             [timedelta(seconds=15), 'b'],
             [timedelta(seconds=10), 'bb'],
             [timedelta(seconds=9), 'b'],
             [timedelta(seconds=8), 'b'],
             [timedelta(seconds=7), 'b'],
             [timedelta(seconds=6), 'b'],
             [timedelta(seconds=5), 'bb'],
             [timedelta(seconds=4), 'b'],
             [timedelta(seconds=3), 'b'],
             [timedelta(seconds=2), 'b'],
             [timedelta(seconds=1), 'b'],
             [timedelta(seconds=0), 'Lb']]
beepC2 = [False for i in range(23)]
beepC3 = [False for i in range(23)]
C2Started = False
C3Started = False

noTot = False


def getData():
    global C1, C2, C3, C4
    global Altitude, Azimuth
    global noTot
    _town = ''
    _height = ''
    _url = ''
    _locName = ''
    _long = ['', '', '', '']
    _lat = ['', '', '', '']
    # load data
    _load = input(
        'To get data online enter [0], to load location data enter [1]: ')
    if _load is '1':
        _locName = input('Enter location name: ')
        _locNameFull = os.path.dirname(
            sys.argv[0]) + '/eclipseLocation_' + _locName + '.p'
        if os.path.exists(_locNameFull):
            [C1, C2, C3, C4, Altitude, Azimuth] = pickle.load(
                open(_locNameFull, 'rb'))
            return
        else:
            print('WARNING: location is not saved!')
            raise NameError
    elif _load is '0':
        pass
    else:
        raise ValueError  # Invalid input
    # check internet connection
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', 'google.com')
    except BaseException:
        print("ERORR: No internet connection!")
        print("You may enter the times manually in the code")
        raise SystemExit
    # get location information
    _townLoc = input(
        'To enter US town name enter [0], to enter location enter [1]: ')
    if _townLoc is '0':
        _town = input('Enter US town name [e.g. Salem, OR]: ')
        _height = input('Enter height (-90 to 10999)meters)= ')
        _url = 'http://aa.usno.navy.mil/solareclipse?eclipse=22017' +\
            '&state=' + _town.split(',')[1].strip() +\
            '&place=' + _town.split(',')[0].strip() +\
            '&height=' + _height
    elif _townLoc is '1':
        print('\n')
        print('Enter Longitude:')
        _long[0] = input('[E/W]? ')
        if _long[0] in ['e', 'E']:
            _long[0] = '1'
        elif _long[0] in ['w', 'W']:
            _long[0] = '-1'
        else:
            raise ValueError  # Invalid input
        _long[1] = input('arcdegree [int]= ')
        _long[2] = input('arcminute [int]= ')
        _long[3] = input('arcsecond [int/float]= ')
        print('\n')
        print('Enter Latitude:')
        _lat[0] = input('[N/S]? ')
        if _lat[0] in ['n', 'N']:
            _lat[0] = '1'
        elif _lat[0] in ['s', 'S']:
            _lat[0] = '-1'
        else:
            raise ValueError  # Invalid input
        _lat[1] = input('arcdegree [int]= ')
        _lat[2] = input('arcminute [int]= ')
        _lat[3] = input('arcsecond [int/float]= ')
        _height = input('Enter height (-90 to 10999)meters)= ')
        _url = 'http://aa.usno.navy.mil/solareclipse?eclipse=22017&place=' +\
            '&lon_sign=' + _long[0] +\
            '&lon_deg=' + _long[1] +\
            '&lon_min=' + _long[2] +\
            '&lon_sec=' + _long[3] +\
            '&lat_sign=' + _lat[0] +\
            '&lat_deg=' + _lat[1] +\
            '&lat_min=' + _lat[2] +\
            '&lat_sec=' + _lat[3] +\
            '&height=' + _height
    else:
        raise ValueError  # Invalid input

    if int(_height) < -90 or int(_height) > 10999:
        print('ERORR: Invalid height, height must be between -90 to 10999 meters')
        raise SystemExit
    http = urllib3.PoolManager()
    r = http.request('GET', _url)
    data = (r.data).decode('utf-8')
    if data.find('Error') != -1:
        print("ERROR: Location not found!")
        raise SystemExit
    if data.find('Totality Begins') == -1:
        print("WARNING: NO totality in your location!")
        noTot = True
    # Setting C1
    _info = data[data.find('Eclipse Begins'):data.find(
        'Totality Begins')].split('</td><td>')
    _time = _info[2].split(':')
    C1 = C1.replace(year=2017,
                    month=8,
                    day=int(_info[1]),
                    hour=int(_time[0]),
                    minute=int(_time[1]),
                    second=int(_time[2].split('.')[0]),
                    microsecond=int(_time[2].split('.')[1]) * 100000)
    Altitude[0] = _info[3]
    Azimuth[0] = _info[4]
    # Setting C2
    if noTot:
        C2 = None
    else:
        _info = data[data.find('Totality Begins'):data.find(
            'Maximum Eclipse')].split('</td><td>')
        _time = _info[2].split(':')
        C2 = C2.replace(year=2017,
                        month=8,
                        day=int(_info[1]),
                        hour=int(_time[0]),
                        minute=int(_time[1]),
                        second=int(_time[2].split('.')[0]),
                        microsecond=int(_time[2].split('.')[1]) * 100000)
    Altitude[1] = _info[3]
    Azimuth[1] = _info[4]
    # Setting C3
    if noTot:
        C3 = None
    else:
        _info = data[data.find('Totality Ends'):data.find(
            'Eclipse Ends')].split('</td><td>')
        _time = _info[2].split(':')
        C3 = C3.replace(year=2017,
                        month=8,
                        day=int(_info[1]),
                        hour=int(_time[0]),
                        minute=int(_time[1]),
                        second=int(_time[2].split('.')[0]),
                        microsecond=int(_time[2].split('.')[1]) * 100000)
    Altitude[2] = _info[3]
    Azimuth[2] = _info[4]
    # Setting C4
    _info = data[data.find('Eclipse Ends'):data.find(
        '</table><br>')].split('</td><td>')
    _time = _info[2].split(':')
    C4 = C4.replace(year=2017,
                    month=8,
                    day=int(_info[1]),
                    hour=int(_time[0]),
                    minute=int(_time[1]),
                    second=int(_time[2].split('.')[0]),
                    microsecond=int(_time[2].split('.')[1]) * 100000)
    Altitude[3] = _info[3]
    Azimuth[3] = _info[4]
    print("Data loaded succesfully!")
    _save = input('Do you want to save in file for future use [Y/n]? ')
    if _save in ['y', 'Y', '']:
        _locName = input(
            'Enter location name (without space) for future use: ')
        _locNameFull = os.path.dirname(
            sys.argv[0]) + '/eclipseLocation_' + _locName + '.p'
        if os.path.exists(_locNameFull):
            print('WARNING: location already exists!')
            raise NameError
        pickle.dump([C1, C2, C3, C4, Altitude, Azimuth],
                    open(_locNameFull, 'wb'))
        print('Location ' + _locName + ' saved succesfully!')
        input('Press any key to continue...')
    elif _save in ['n', 'N']:
        pass
    else:
        raise ValueError  # Invalid input!


def calculateLocalTimes():
    global C1L, C2L, C3L, C4L
    _from_zone = tz.tzutc()
    _to_zone = tz.tzlocal()
    _tmpTime = C1.replace(tzinfo=_from_zone)
    C1L = _tmpTime.astimezone(_to_zone)
    if C2 is not None:
        _tmpTime = C2.replace(tzinfo=_from_zone)
        C2L = _tmpTime.astimezone(_to_zone)
        _tmpTime = C3.replace(tzinfo=_from_zone)
        C3L = _tmpTime.astimezone(_to_zone)
    _tmpTime = C4.replace(tzinfo=_from_zone)
    C4L = _tmpTime.astimezone(_to_zone)


def beep(mode):
    if mode is 'Lb':
        bashCommand = "beep -f 261 -l 1000"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        return
    elif mode is 'b':
        _repeat = 1
    elif mode is 'bb':
        _repeat = 2
    elif mode is 'bbb':
        _repeat = 3
    else:
        raise ValueError  # beep mode is not valid
    bashCommand = "beep -f 261 -r " + str(_repeat) + " -d 25 -l 100"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)


def beeper(nowTime, endTime, c):
    global C2Started
    global C3Started
    global beepTimes
    global beepC2
    global beepC3
    _deltaTime = endTime - nowTime + timedelta(seconds=-1)
    if c == 'C2':
        if not C2Started:
            for i in range(len(beepTimes)):
                if beepTimes[i][0] > _deltaTime:
                    beepC2[i] = True
            C2Started = True
        else:
            for i in range(len(beepTimes)):
                if beepTimes[i][0] > _deltaTime and not beepC2[i]:
                    beepC2[i] = True
                    beep(beepTimes[i][1])
    if c == 'C3':
        if not C3Started:
            for i in range(len(beepTimes)):
                if beepTimes[i][0] > _deltaTime:
                    beepC3[i] = True
            C3Started = True
        else:
            for i in range(len(beepTimes)):
                if beepTimes[i][0] > _deltaTime and not beepC3[i]:
                    beepC3[i] = True
                    beep(beepTimes[i][1])


def mainLoop(window):
    while True:
        now = datetime.utcnow()
        window.clear()
        window.addstr(4, 1, "Local Time: ")
        window.addstr(4, 15, datetime.now().strftime("%H:%M:%S"))
        window.addstr(5, 1, "UTC Time: ")
        window.addstr(5, 15, now.strftime("%H:%M:%S"))
        if C2 is None:
            window.addstr(3, 44, "NO TOTALITY")
            window.addstr(4, 42, "at this location")
        else:
            window.addstr(13, 37, "Duration of Totality:")
            window.addstr(14, 42, str(C3 - C2)[:-5])
        if now < C1:
            window.addstr(1, 1, "Time to C1: ")
            window.addstr(1, 20, str(C1 - now)[:-7])
            _l0 = 7
            window.addstr(_l0, 10, "UTC")
            window.addstr(_l0, 18, "Computer Time")
            window.addstr(_l0, 35, "Alt.")
            window.addstr(_l0, 45, "Azi.")
            _l0 += 1
            window.addstr(_l0, 1, "C1: ")
            window.addstr(_l0, 8, C1.strftime("%H:%M:%S"))
            window.addstr(_l0, 20, C1L.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, Altitude[0])
            window.addstr(_l0, 45, Azimuth[0])
            if C2 is not None:
                _l0 += 1
                window.addstr(_l0, 1, "C2: ")
                window.addstr(_l0, 8, C2.strftime("%H:%M:%S"))
                window.addstr(_l0, 20, C2L.strftime("%H:%M:%S"))
                window.addstr(_l0, 35, Altitude[1])
                window.addstr(_l0, 45, Azimuth[1])
                _l0 += 1
                window.addstr(_l0, 1, "C3: ")
                window.addstr(_l0, 8, C3.strftime("%H:%M:%S"))
                window.addstr(_l0, 20, C3L.strftime("%H:%M:%S"))
                window.addstr(_l0, 35, Altitude[2])
                window.addstr(_l0, 45, Azimuth[2])
            _l0 += 1
            window.addstr(_l0, 1, "C4: ")
            window.addstr(_l0, 8, C4.strftime("%H:%M:%S"))
            window.addstr(_l0, 20, C4L.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, Altitude[3])
            window.addstr(_l0, 45, Azimuth[3])
        elif now < C2 and C2 is not None:
            window.addstr(1, 1, "Time to to C2: ")
            window.addstr(1, 20, str(C2 - now)[:-7])
            _l0 = 7
            window.addstr(_l0, 18, "UTC")
            window.addstr(_l0, 30, "UTC")
            _l0 += 1
            window.addstr(_l0, 1, "C2: ")
            window.addstr(_l0, 15, C2.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C2L.strftime("%H:%M:%S"))
            _l0 += 1
            window.addstr(_l0, 1, "C3: ")
            window.addstr(_l0, 15, C3.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C3L.strftime("%H:%M:%S"))
            _l0 += 1
            window.addstr(_l0, 1, "C4: ")
            window.addstr(_l0, 15, C4.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C4L.strftime("%H:%M:%S"))
            beeper(now, C2, 'C2')
        elif now < C3 and C3 is not None:
            window.addstr(1, 1, "Time to to C3: ")
            window.addstr(1, 20, str(C3 - now)[:-7])
            _l0 = 7
            window.addstr(_l0, 18, "UTC")
            window.addstr(_l0, 30, "UTC")
            _l0 += 1
            window.addstr(_l0, 1, "C3: ")
            window.addstr(_l0, 15, C3.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C3L.strftime("%H:%M:%S"))
            _l0 += 1
            window.addstr(_l0, 1, "C4: ")
            window.addstr(_l0, 15, C4.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C4L.strftime("%H:%M:%S"))
            beeper(now, C3, 'C3')
        elif now < C4:
            window.addstr(1, 1, "Time to to C4: ")
            window.addstr(1, 20, str(C4 - now)[:-7])
            _l0 = 7
            window.addstr(_l0, 18, "UTC")
            window.addstr(_l0, 30, "UTC")
            _l0 += 1
            window.addstr(_l0, 1, "C4: ")
            window.addstr(_l0, 15, C4.strftime("%H:%M:%S"))
            window.addstr(_l0, 35, C4L.strftime("%H:%M:%S"))
        else:
            window.addstr(7, 1, "Eclipse has ended!")
        curses.curs_set(0)
        window.refresh()
        time.sleep(0.01)


def main():

    if GetLocation:
        getData()

    calculateLocalTimes()

    curses.wrapper(mainLoop)


if __name__ == '__main__':
    main()
