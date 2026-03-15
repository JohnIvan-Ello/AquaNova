import time
import config
from config import gps_serial, gps_lat, gps_lon

def nmea_dm_to_dd(dm_str, hemi):
    try:
        v = float(dm_str)
    except (TypeError, ValueError):
        return None
    deg = int(v // 100)
    minutes = v - deg * 100
    dd = deg + minutes / 60.0
    if hemi in ('S', 'W'):
        dd = -dd
    return dd

def gps_thread():
    global gps_lat, gps_lon, gps_serial
    while True:
        try:
            if not gps_serial:
                time.sleep(1)
                continue

            line = gps_serial.readline().decode("ascii", errors="ignore").strip()
            if not line or not line.startswith('$'):
                continue

            if line.startswith(('$GPRMC', '$GNRMC')):
                f = line.split(',')
                if len(f) > 6 and f[2] == 'A':
                    lat = nmea_dm_to_dd(f[3], f[4])
                    lon = nmea_dm_to_dd(f[5], f[6])
                    if lat and lon:
                        config.gps_lat, config.gps_lon = lat, lon
                        #print(f"[GPS] RMC fix: {gps_lat:.6f}, {gps_lon:.6f}")
            elif line.startswith(('$GPGGA', '$GNGGA')):
                f = line.split(',')
                if len(f) > 5 and f[6] not in ('0', ''):
                    lat = nmea_dm_to_dd(f[2], f[3])
                    lon = nmea_dm_to_dd(f[4], f[5])
                    if lat and lon:
                        config.gps_lat, config.gps_lon = lat, lon
                        #print(f"[GPS] GGA fix: {gps_lat:.6f}, {gps_lon:.6f}")
        except Exception as e:
            print(f"[GPS] thread error: {e}")
            time.sleep(1)
