# -*- coding: utf-8 -*-

class PLCGlobals():
    def __init__(self):
        pass

    SIGNAL_NOT_CONNECT= 0b1111111111
    FILE_NOT_FOUND=     0b1111111110
    CLOSE_CSV_OK =      0b111111111
    CLOSE_CSV_FAIL =    0b111111110
    SAVE_CSV_OK =       0b11111111
    SAVE_CSV_FAIL =     0b11111110
    FILE_EOF =          0b1111111
    WRITE_OK =          0b111111
    WRITE_FAIL =        0b111110
    READ_OK =           0b11111
    READ_FAIL =         0b01111
    NEXT_OK =           0b111
    NEXT_FAIL =         0b011
    OPEN_DICT_OK =      0b110
    OPEN_DICT_FAIL =    0b10
    OPEN_CSV_OK =       0b1
    OPEN_CSV_FAIL =     0b0
    UPDATE_OK =         0b100
    UPDATE_FAIL =       0b101
    SET_VAL_OK =        0b10
    SET_VAL_FAIL =      0b01

    BREAK_DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    debug = 1
    PORT = 8889
    host = "localhost"
    PATH = "С:\\Users\User\\Beremiz\\beremiz_workdir\\"
