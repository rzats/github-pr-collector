from datetime import datetime


def unix_2_utc(unix_timestamp):
    """
    Turns a Unix timestamp into a UTC timestamp string.

    @param unix_timestamp: Unix timestamp.
    @return: Corresponding timestamp string
    """
    return datetime.utcfromtimestamp(unix_timestamp) \
        .strftime('%Y-%m-%dT%H:%M:%SZ')


def utc_2_datetime(utc_timestamp):
    """
    Turns an UTC timestamp string into a datetime object.

    @param utc_timestamp: UTC timestamp string.
    @return: Corresponding datetime object
    """
    return datetime.strptime(utc_timestamp, '%Y-%m-%dT%H:%M:%SZ')


def seconds_2_human(seconds):
    """
    Turns a number of seconds into a "human-readable" date diff.

    @param seconds: Number of seconds.
    @return: Date difference string.
    """
    seconds_to_minute = 60
    seconds_to_hour = 60 * seconds_to_minute
    seconds_to_day = 24 * seconds_to_hour

    (days, remainder) = divmod(seconds, seconds_to_day)
    (hours, remainder) = divmod(remainder, seconds_to_hour)
    (minutes, secs) = divmod(remainder, seconds_to_minute)

    return f"{days:.0f} day(s), {hours:.0f} hour(s), " + \
           f"{minutes:.0f} minute(s), {secs:.0f} second(s)"
