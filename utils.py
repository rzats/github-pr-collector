from datetime import datetime

def unix_2_utc(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

def utc_2_datetime(utc_timestamp):
    return datetime.strptime(utc_timestamp, '%Y-%m-%dT%H:%M:%SZ')