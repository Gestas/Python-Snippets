import logging
from datetime import datetime

import iso8601
import rfc3339
# pip install python-dateutil
from dateutil import tz

logger = logging.getLogger(__name__)


class DateTimeFormatter:
    """One datetime formatter to rule them all."""

    def __init__(self):
        self._usa_format_12 = "%m/%d/%Y %I:%M:%S"
        self._usa_format_24 = "%m/%d/%Y %H:%M:%S"
        self._global_format_12 = "%d/%m/%Y %H:%M:%S"
        self._global_format_24 = "%d/%m/%Y %I:%M:%S"

    def global12(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._global_format_12)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._global_format_12)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._global_format_12)

    def global24(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._global_format_24)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._global_format_24)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._global_format_24)

    def usa12(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._usa_format_12)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._usa_format_12)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._usa_format_12)

    def usa24(self, dt=None):
        if not dt:
            return datetime.now().strftime(self._usa_format_24)
        try:
            return datetime.fromtimestamp(float(dt)).strftime(self._usa_format_24)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.strftime(self._usa_format_24)

    @staticmethod
    def r3339(dt=None):
        if not dt:
            return rfc3339.rfc3339(datetime.utcnow())
        try:
            return rfc3339.rfc3339(datetime.fromtimestamp(float(dt)))
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return rfc3339.rfc3339(_i)

    @staticmethod
    def i8601(dt=None):
        if not dt:
            return datetime.isoformat(datetime.utcnow())
        try:
            return datetime.isoformat(datetime.fromtimestamp(float(dt)))
        except (TypeError, ValueError):
            return iso8601.parse_date(str(dt))

    @staticmethod
    def epoch(dt=None):
        if not dt:
            return datetime.now().timestamp()
        try:
            return float(dt)
        except (TypeError, ValueError):
            _i = iso8601.parse_date(str(dt))
            return _i.timestamp()

    @staticmethod
    def utc_to_local(utc_dt: datetime):
        """Convert a UTC datetime to a local timezone aware datetime.

        :param utc_dt: Datetime using the UTC timezone
        :type utc_dt: datetime
        :return: Parameter datetime adjusted to use the local timezone
        :rtype: datetime
        """
        utc_dt = utc_dt.replace(tzinfo=tz.gettz("UTC"))
        return utc_dt.astimezone(tz.tzlocal())

    @staticmethod
    def local_to_utc(local_dt):
        """Convert a local datetime to a UTC timezone aware datetime.

        :param local_dt: Datetime using the local timezone
        :type local_dt: datetime
        :return: Parameter datetime adjusted to use the UTC timezone
        :rtype: datetime
        """
        local_dt = local_dt.replace(tzinfo=tz.tzlocal())
        return local_dt.astimezone(tz.tzlocal())

    @staticmethod
    def tz_to_tz(dt, source_tz, dest_tz):
        """Covert a datetime object from <timezone> to <timezone>.

        :param dt: A datetime
        :type dt: datetime
        :param source_tz: The timezone of the supplied datetime
        :type source_tz: str
        :param dest_tz: The timezone to convert to
        :type dest_tz: str
        :return: A datetime
        :rtype: datetime
        """
        dt = dt.replace(tzinfo=tz.gettz(source_tz))
        return dt.replace(tzinfo=tz.gettz(dest_tz))
