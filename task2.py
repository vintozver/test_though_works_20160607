#!/usr/bin/env python3

import sys
import re
import operator
import functools


class Conference(object):
    def __init__(self):
        self.sessions = list()
        self.session_pointer = -1

    def add_item(self, item, duration):
        pass

    def remove_item(self, item, duration):
        pass

    def is_valid(self):
        return functools.reduce(operator.and_, map(lambda session: session.is_valid(), self.sessions))

class Session(object):
    @staticmethod
    def raw_duration(duration):
        return duration == 'lightning' and 5 or duration

    def __init__(self):
        self.items = list()
        self.duration = 0

    def add(self, item, duration):
        self.items.append((item, duration))
        self.duration += self.raw_duration(duration)

    def remove(self, item, duration):
        self.items.pop((item, duration))
        self.duration -= self.raw_duration(duration)

    def try_add(self, item, duration):
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError


class MorningSession(Session):
    def try_add(self, item, duration):
        if self.duration + self.raw_duration(duration) <= 180:
            self.add(item, duration)
            return True
        else:
            return False

    def is_valid(self):
        return self.duration == 180


class EveningSession(Session):
    def try_add(self, item, duration):
        if self.duration + self.raw_duration(duration) <= 240:
            self.add(item, duration)
            return True
        else:
            return False

    def is_valid(self):
        return 180 <= self.duration <= 240


class Track(object):
    def __init__(self, session1, session2):
        self.session1 = session1
        self.session2 = session2

    def is_valid(self):
        return self.session1.is_valid() and self.session2.is_valid()


class ScheduleRequest(object):
    def __init__(self, items):
        self.items = items or list()

    @classmethod
    def from_lines(cls, lines):
        def parser():
            re_line = re.compile('.*\\b((\\d+)|(lightning)).*')
            for line in lines:
                line = line.strip()
                re_line_match = re_line.match(line)
                if re_line_match is None:
                    raise AssertionError('Unexpected input', line)
                duration = re_line_match.group(1)
                if duration != 'lightning':
                    try:
                        duration = int(duration)
                    except (TypeError, ValueError):
                        raise AssertionError('Duration value is not expected')
                yield line, duration
        return cls(list(parser()))


class ScheduleRequestException(Exception):
    pass


def main():
    schedule_request = ScheduleRequest.from_lines(sys.stdin.readlines())
    print(schedule_request.items)

if __name__ == '__main__':
    main()


# Test command (sh, bash)
# $ cat task2.1.dat | ./task2.py
