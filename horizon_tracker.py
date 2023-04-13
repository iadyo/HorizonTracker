# Nieskończone, pozycja słońca - Python
# Stworzone przez Adrian 'adyo' Just

import argparse, datetime
from os import system
from time import sleep
from math import *

def julian_day(year, month, day, hour, minutes, seconds, ms):
    L1 = year + 4716 - int((14 - month) / 12)
    M1 = (month + 9) % 12
    G = int(0.75 * int((L1 + 184) / 100)) - 38
    return (int(365.25 * L1) + int(30.6 * M1 + 0.4) + day - G - 1402) - 0.5 + hour / 24 + minutes / 24 / 60 + seconds / 24 / 3600 + ms / 24 / 3600 / 1000000

def is_leap_year(year):
    return ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0))

def hhmmss(value):
    hh = value // 15
    mm = int((value / 15 - hh) * 60)
    ss = value / 15 * 3600 - hh * 3600 - mm * 60
    return hh + 2, mm, ss

def convert_time(x):
    return '{:02d}:{:02d}:{:02d}'.format(int(hhmmss(x)[0]), int(hhmmss(x)[1]), int(hhmmss(x)[2]))

def calc_sun_pos(lat, lon, dutc):
    hour = dutc.hour + dutc.minute / 60 + dutc.second / 3600 + dutc.microsecond / 3600000000
    doy = dutc.timetuple().tm_yday

    if is_leap_year(dutc.year): gamma = ((2 * pi) / 366) * (doy - 1 + ((hour - 12) / 24))
    else: gamma = ((2 * pi) / 365) * (doy - 1 + ((hour - 12) / 24))

    eqtime = 229.18 * (0.000075 + 0.001868 * cos(gamma) - 0.032077 * sin(gamma) - 0.014615 * cos(2 * gamma) - 0.040849 * sin(2 * gamma))
    decl = degrees(0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma) - 0.006758 * cos(2 * gamma) + 0.000907 * sin(2 * gamma) - 0.002697 * cos(3 * gamma) + 0.00148 * sin(3 * gamma))
    time_offset = eqtime + 4 * lon - 60 * 1
    tst = hour * 60 + dutc.minute + dutc.second / 60 + dutc.microsecond / 3600000000 * 60 + time_offset
    ha = tst / 4 - 180
    alt = degrees(asin(sin(radians(decl)) * sin(radians(lat)) + cos(radians(decl)) * cos(radians(lat)) * cos(radians(ha))))
    ha = degrees(acos(cos(radians(90.833)) / (cos(radians(lat)) * cos(radians(decl))) - tan(radians(lat)) * tan(radians(decl))))
    sunrise = (720 - 4 * (lon + ha) - eqtime) / 60 * 15
    snoon = (720 - 4 * (lon - ha) - eqtime) / 60 * 15

    if alt >= -0.833:
        if alt < 0:
            alt = str(alt) + ' (night)'
        elif alt < 6:
            alt = str(alt) + ' (nautical twilight)'
        elif alt < 12:
            alt = str(alt) + ' (civil twilight)'
        else: alt = str(alt) + ' (day)'
    else: alt = str(alt) + ' (night)'
    day_len = convert_time(snoon - sunrise)
    
    print('\n\tAltitude: {}'.format(alt))
    print('\tLenght of the day: {}'.format(day_len))
    print('\tSunrise: {}'.format(convert_time(sunrise)))
    print('\tSnoon: {}'.format(convert_time(snoon)))

def get_moon_data(year, month, day, lat, lon):
    import ephem
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = f'{year}/{month}/{day}'
    moon = ephem.Moon(obs)

    illumination = moon.moon_phase
    phase = ''

    if illumination < 0.025 or illumination > 0.975:
        phase = 'New Moon' if illumination < 0.025 else 'Full Moon'
    elif illumination < 0.25:
        phase = 'Waxing Crescent'
    elif illumination < 0.375:
        phase = 'First Quarter'
    elif illumination < 0.625:
        phase = 'Waxing Gibbous'
    elif illumination < 0.75:
        phase = 'Third Quarter'
    else:
        phase = 'Waning Gibbous'

    print('\n\tLunar Phase: {}'.format(phase))
    print('\tIllumination: {:.1f}%'.format(illumination * 100))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-lat', dest='latitude', help='set latitude', type=float, default=51.110550)
    parser.add_argument('-lon', dest='longitude', help='set longitude', type=float, default=17.025560)
    parser.add_argument('-ref', dest='refresh', help='set the refresh time', type=float, default=0.3)
    parser.add_argument('--lunar', help='show lunar info', action='store_true')
    parser.add_argument('--date', help='set date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(), default=datetime.date.today(), nargs='?')
    args = parser.parse_args()

    try:
        current_date = args.date or datetime.date.today()
        while True:
            system('cls')
            dutc = datetime.datetime.utcnow()
            current_time = datetime.datetime.now().time()
            dl = datetime.datetime.combine(current_date, current_time)
            year, month, day = dl.year, dl.month, dl.day
            hour, minutes, seconds, ms = dl.time().hour, dl.time().minute, dl.time().second, dl.time().microsecond
            jl = julian_day(year, month, day, hour, minutes, seconds, ms)

            print('\n\tLocal Time: {}'.format(dl))
            print('\tUniversal Time: {}'.format(dutc))
            print('\tJulian Day: {}'.format(jl))
            calc_sun_pos(args.latitude, args.longitude, dl)

            if args.lunar: get_moon_data(year, month, day, args.latitude, args.longitude)
            if args.refresh == 0.: break
            else: sleep(args.refresh)
    except KeyboardInterrupt:
        print('Zatrzymano przez użytkownika!')
