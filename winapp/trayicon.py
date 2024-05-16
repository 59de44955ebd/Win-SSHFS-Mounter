from ctypes import Union, Structure, c_ubyte, sizeof, byref
from ctypes.wintypes import UINT, DWORD, HWND, WCHAR, HICON

from winapp.const import *
from winapp.dlls import shell32


class TimeoutVersionUnion(Union):
    _fields_ = [('uTimeout', UINT),
                ('uVersion', UINT),]

class NOTIFYICONDATAW(Structure):
    def __init__(self, *args, **kwargs):
        super(NOTIFYICONDATAW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize', DWORD),
        ('hWnd', HWND),
        ('uID', UINT),
        ('uFlags', UINT),
        ('uCallbackMessage', UINT),
        ('hIcon', HICON),
        ('szTip', WCHAR * 128),
        ('dwState', DWORD),
        ('dwStateMask', DWORD),
        ('szInfo', WCHAR * 256),
        ('uTimeout', UINT),  # ('union', TimeoutVersionUnion),
        ('szInfoTitle', WCHAR * 64),
        ('dwInfoFlags', DWORD),
        ('guidItem', c_ubyte * 16),  # GUID
        ('hBalloonIcon', HICON),
    ]

ID_TRAYICON = 300

class TrayIcon(object):

    def __init__(self, parent_window, hicon, window_title, message_id, show=True):
        self.trayiconinfo = NOTIFYICONDATAW()
        self.trayiconinfo.hWnd = parent_window.hwnd
        self.trayiconinfo.uID = ID_TRAYICON
        self.trayiconinfo.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP | NIF_SHOWTIP
        self.trayiconinfo.uCallbackMessage = message_id
        self.trayiconinfo.hIcon = hicon
        self.trayiconinfo.szTip = window_title
        self.trayiconinfo.dwState = NIS_SHAREDICON
        self.trayiconinfo.szInfo = window_title
        self.trayiconinfo.uTimeout = 5000
        #self.trayiconinfo.union.uTimeout = 5000
        #self.trayiconinfo.union.uVersion = NOTIFYICON_VERSION
        self.trayiconinfo.dwInfoFlags = NIIF_INFO
        self.trayiconinfo.hBalloonIcon = 0
        if show:
            self.show()

    def __del__(self):
        shell32.Shell_NotifyIconW(NIM_DELETE, byref(self.trayiconinfo))

    def show(self, flag=True):
        shell32.Shell_NotifyIconW(NIM_ADD if flag else NIM_DELETE, byref(self.trayiconinfo))
