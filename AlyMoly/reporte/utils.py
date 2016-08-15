#-*- encoding: UTF-8 -*-

class Enumerate(object):
    def __init__(self, names, token=' '):
        for number, name in enumerate(names.split(token)):
            setattr(self, name, number)
