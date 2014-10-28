__author__ = 'Yorick Chollet'

import logging

from datetime import datetime, timedelta
from dateutil.parser import parse as parse_datestr
from dateutil.tz import tzutc
from urlparse import urlparse

from conf.constants import DATEFMT, HTTPRE
from errors.urierror import URIRequestError
from errors.dateerror import DateTimeError


def validate_req_datetime(datestr, strict=True):
    """
    Parses the requested date string into a dateutil time object
    Raises DateTimeError if the parse fails to produce a datetime.
    :param datestr: A date string, in a common format.
    :return: the dateutil time object
    """
    try:
        if strict:
            date = datetime.strptime(datestr, DATEFMT)
        else:
            date = parse_datestr(datestr, fuzzy=True)
        logging.debug("Accept datetime parsed to: "+date_str(date))
        return date.replace(tzinfo=tzutc())
    except Exception as e:
        raise DateTimeError("Error parsing 'Accept-Datetime: %s' \n"
                            "Message: %s" % (datestr, e.message))


def validate_req_uri(pathstr, methodstr):
    """
    Parses the requested URI string.
    Raises URIRequestError if the parse fails to recognize a valid URI
    :param urlstr: A URI string, in a common format.
    :return: the URI string object
    """

    try:
        #removes leading 'method/' and replaces whitespaces
        path = pathstr[len(methodstr+'/'):].replace(' ', '%20')

        # Trying to fix incomplete URI
        if not bool(HTTPRE.match(path)):
            # if not bool(WWWRE.match(path)):
            #     path = 'www.'+path TODO remove?
            path = 'http://'+path

        uri = validate_uristr(path)
        logging.debug("Requested URI parsed to: "+uri)
        return uri
    except Exception as e:
        raise URIRequestError("Error: Cannot parse requested path '%s' \n"
                              "message: %s" % (pathstr, e.message))


def validate_uristr(uristr):
    """
    Controls and validates the uri string.
    :param uristr: The uri string that needs to be verified
    :return: The validated uri string. Raises an Exception if it is not valid.
    """
    try:
        return str(urlparse(uristr).geturl())
    except Exception as e:
        raise Exception("Error: cannot parse uri string %s" % uristr)

def validate_date(datestr, strict=False):
    """
    Controls and validates the date string.
    :param datestr: The date string representation
    :param strict: When True, the date must strictly follow the format defined
    in the config file (DATEFMT). When False, the date string can be fuzzy and
    the function will try to reconstruct it.
    :return: The datetime object form the parsed date string.
    """
    try:
        if strict:
            date = datetime.strptime(datestr, DATEFMT)
        else:
            date = parse_datestr(datestr, fuzzy=True).replace(tzinfo=tzutc())
        return date
    except Exception as e:
        raise Exception("Error: cannot parse date string %s" % datestr)


def date_str(date, format=DATEFMT):
    """
    Returns a string representation of the date object.
    :param date: the date object which needs to be printed
    :param format: the string format of the date
    By default this is the format specified in the config file
    :return: The formatted date string.
    """
    return date.strftime(format)

def parse_date(*args, **kwargs):
    return parse_datestr(*args, **kwargs)

def nowstr():
    """
    String representation of the current UTC time
    :return: a string representation of the current UTC time
    """
    return date_str(datetime.utcnow()).encode('utf8')


def closest(timemap, accept_datetime, sorted=True):
    """
    Finds the chronologically closest memento
    :param timemap: A sorted Timemap
    :param accept_datetime: the time object
    :param sorted: boolean to indicate if the list is sorted or not.
    :return:
    """

    delta = timedelta.max
    memento = None

    for (url, dt) in timemap:
        diff = abs(accept_datetime - dt)
        if diff < delta:
            memento = url
            delta = diff
        elif sorted:
            # The list is sorted and the delta didn't increase this time.
            # It will not increase anymore: Return the Memento (best one).
            return memento

    return memento


def now():
    """
    Date representation of the current UTC time
    :return: a date representation of the current UTC time
    """
    return datetime.utcnow().replace(tzinfo=tzutc())