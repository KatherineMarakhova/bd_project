from appscript import app


class Outlook(object):
    def __init__(self):
        self.client = app('Microsoft Outlook')
