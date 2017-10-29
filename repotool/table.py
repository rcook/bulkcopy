##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

class Table(object):
    def __init__(self):
        self._max_header_len = 0
        self._rows = []

    def add_row(self, header, content):
        header_len = len(header)
        if header_len > self._max_header_len:
            self._max_header_len = header_len

        self._rows.append((header, content))

    def show(self, indent=0, column_sep=": "):
        indent_str = "  " * indent
        for header, content in self._rows:
            print("{}{}{}{}".format(indent_str, header.ljust(self._max_header_len), column_sep, content))
