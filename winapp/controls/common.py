from ctypes import Structure, POINTER, sizeof
from ctypes.wintypes import HWND, INT, UINT, POINT, LPARAM, DWORD, COLORREF, HDC, RECT, HBRUSH, HPEN, BOOL, BYTE, LONG, WCHAR, HICON
from winapp.const import *
from winapp.wintypes_extended import UINT_PTR, ULONG_PTR, DWORD_PTR


class NMHDR(Structure):
    _pack_ = 8
    _fields_ = [
        ("hwndFrom", HWND),
        ("idFrom", UINT_PTR),
        ("code", INT),
    ]
LPNMHDR = POINTER(NMHDR)

class NMCUSTOMDRAW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwDrawStage", DWORD),
        ("hdc", HDC),
        ("rc", RECT),
        ("dwItemSpec", POINTER(DWORD)),
        ("uItemState", UINT),
        ("lItemlParam", LPARAM),
    ]
LPNMCUSTOMDRAW = POINTER(NMCUSTOMDRAW)

class NMMOUSE(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwItemSpec", DWORD_PTR),
        ("dwItemData", DWORD_PTR),
        ("pt", POINT),
        ("dwHitInfo", LPARAM),
    ]
LPNMMOUSE = POINTER(NMMOUSE)

class COLORSCHEME(Structure):
    def __init__(self, *args, **kwargs):
        super(COLORSCHEME, self).__init__(*args, **kwargs)
        self.dwSize = sizeof(self)
    _fields_ = [
        ("dwSize",                DWORD),
        ("clrBtnHighlight",       COLORREF),
        ("clrBtnShadow",          COLORREF),
    ]

class PAINTSTRUCT(Structure):
    _fields_ = [
        ("hdc",            HDC),
        ("fErase",         BOOL),
        ("rcPaint",        RECT),
        ("fRestore",       BOOL),
        ("fIncUpdate",     BOOL),
        ("rgbReserved",    BYTE * 32),
    ]

class MEASUREITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemWidth", UINT),
        ("itemHeight", UINT),
        ("lItemlParam", ULONG_PTR),
    ]
LPMEASUREITEMSTRUCT = POINTER(MEASUREITEMSTRUCT)

class DRAWITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemAction", UINT),
        ("itemState", UINT),

        ("hwndItem", HWND),
        ("hDC", HDC),
        ("rcItem", RECT),
        ("itemData", ULONG_PTR),
    ]

class TEXTMETRICW(Structure):
    _fields_ = [
        ("tmHeight", 			    LONG),
        ("tmAscent",                LONG),
        ("tmDescent",               LONG),
        ("tmInternalLeading",       LONG),
        ("tmExternalLeading",       LONG),
        ("tmAveCharWidth",          LONG),
        ("tmMaxCharWidth",          LONG),
        ("tmWeight",                LONG),
        ("tmOverhang",              LONG),
        ("tmDigitizedAspectX",      LONG),
        ("tmDigitizedAspectY",      LONG),
        ("tmFirstChar",             WCHAR),
        ("tmLastChar",              WCHAR),
        ("tmDefaultChar",           WCHAR),
        ("tmBreakChar",             WCHAR),
        ("tmItalic",                BYTE),
        ("tmUnderlined",            BYTE),
        ("tmStruckOut",             BYTE),
        ("tmPitchAndFamily",        BYTE),
        ("tmCharSet",               BYTE),
    ]

class SHFILEINFOW(Structure):
    _fields_ = [
        ("hIcon",         HICON),
        ("iIcon",         INT),
        ("dwAttributes",  DWORD),
        ("szDisplayName", WCHAR * MAX_PATH),
        ("szTypeName",    WCHAR * 80),
    ]
