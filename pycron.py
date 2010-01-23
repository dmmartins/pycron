#!/usr/bin/python

import sys
import time

class Log(object):
    '''
    '''

    def write(self, text):
        '''
        Print current time followef by text
        '''
        print '%s (%s)' % (time.ctime()[4:-5], text)

class Cron(object):
    """
    """

    def __init__(self, log=None):
        if log == None:
            self.log = Log()

    def _match(self, value, expr):
        if expr == '*':
            return True
        values = expr.split(',')
        for v in values:
            if int(v) == value:
                return True
        return False

    def _calc_next_time(self):
        '''
        Calculate next time with exact seconds.
        '''
        tt = time.localtime(time.time() + 60)
        tt = tt[:5] + (0,) + tt[6:]
        return time.mktime(tt)

    def start(self):
        """
        The cron daemon
        """
        self.log.write('PyCron started')

        while True:
            next_time = self._calc_next_time()

            # Sleep for the time remaining until the next exact minute
            current_time = time.time()

            if current_time < next_time:
                time.sleep(next_time-current_time)

            #
            now = time.localtime(next_time)

            line_number = 1
            for line in self.lines:
                if not line.split() or line.startswith('#'):
                    continue

                try:
                    minute, hour, day, month, weekday, command = line.split()
                except ValueError:
                    self.log.write('error parsing line %i' % (line_number))
                    continue

                # See if the cron entry matches the current time
                # minute
                time_match = self._match(now.tm_min, minute)
                # hour
                time_match = time_match and self._match(now.tm_hour, hour)
                # day
                time_match = time_match and self._match(now.tm_mday, day)
                # month
                time_match = time_match and self._match(now.tm_mon, month)
                # weekday (in crontab 0 or 7 is Sunday)
                match_weekday = self._match(now.tm_wday + 1, weekday) or (now.tm_wday == 7 and self._match(0, weekday))
                time_match = time_match and match_weekday

                if time_match:
                    self.command(command)
                    self.log.write(command)

                line_number = line_number + 1


class CrondTxt(Cron):
    def __init__(self, text, command):
        Cron.__init__(self)

        self.lines = text.split('\n')

        # Command. Must be a callable object
        self.command = command

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: %s <filename> ' % (sys.argv[0])
        exit()

    text = open(sys.argv[1]).read()
    c = CrondTxt(text, lambda x:None)
    c.start()

