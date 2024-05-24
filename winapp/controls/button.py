# https://learn.microsoft.com/en-us/windows/win32/controls/buttons

from ctypes import *
from ctypes.wintypes import HANDLE, RECT, UINT

from winapp.const import *
from winapp.wintypes_extended import MAKELPARAM
from winapp.window import Window
from winapp.dlls import gdi32, user32, uxtheme
from winapp.controls.static import Static, SS_SIMPLE
from winapp.themes import BG_COLOR_DARK, TEXT_COLOR_DARK, BG_BRUSH_DARK


########################################
# Macros
########################################
Button_GetIdealSize = lambda hwnd, psize: user32.SendMessageW(hwnd, BCM_GETIDEALSIZE, 0, psize)
Button_SetImageList = lambda hwnd, pbuttonImagelist: user32.SendMessageW(hwnd, BCM_SETIMAGELIST, 0, pbuttonImagelist)
Button_GetImageList = lambda hwnd, pbuttonImagelist: user32.SendMessageW(hwnd, BCM_GETIMAGELIST, 0, pbuttonImagelist)
Button_SetTextMargin = lambda hwnd, pmargin: user32.SendMessageW(hwnd, BCM_SETTEXTMARGIN, 0, pmargin)
Button_GetTextMargin = lambda hwnd, pmargin: user32.SendMessageW(hwnd, BCM_GETTEXTMARGIN, 0, pmargin)

Button_SetDropDownState = lambda hwnd, fDropDown: user32.SendMessageW(hwnd, BCM_SETDROPDOWNSTATE, fDropDown, 0)
Button_SetSplitInfo = lambda hwnd, pInfo: user32.SendMessageW(hwnd, BCM_SETSPLITINFO, 0, pInfo)
Button_GetSplitInfo = lambda hwnd, pInfo: user32.SendMessageW(hwnd, BCM_GETSPLITINFO, 0, pInfo)
Button_SetNote = lambda hwnd, psz: user32.SendMessageW(hwnd, BCM_SETNOTE, 0, psz)
Button_GetNote = lambda hwnd, psz, pcc: user32.SendMessageW(hwnd, BCM_GETNOTE, pcc, psz)
Button_GetNoteLength = lambda hwnd: user32.SendMessageW(hwnd, BCM_GETNOTELENGTH, 0, 0)
Button_SetElevationRequiredStat = lambda hwnd, fRequired: user32.SendMessageW(hwnd, BCM_SETSHIELD, 0, fRequired)

Button_Enable = lambda hwndCtl, fEnable:         user32.EnableWindow(hwndCtl, fEnable)
Button_GetText = lambda hwndCtl, lpch, cchMax:   user32.GetWindowText(hwndCtl, lpch, cchMax)
Button_GetTextLength = lambda hwndCtl:           user32.GetWindowTextLength(hwndCtl)
Button_SetText = lambda hwndCtl, lpsz:           user32.SetWindowText(hwndCtl, lpsz)

BST_UNCHECKED      =0x0000
BST_CHECKED        =0x0001
BST_INDETERMINATE  =0x0002
BST_PUSHED         =0x0004
BST_FOCUS          =0x0008

Button_GetCheck = lambda hwndCtl:            user32.SendMessageW(hwndCtl, BM_GETCHECK, 0, 0)
Button_SetCheck = lambda hwndCtl, check:     user32.SendMessageW(hwndCtl, BM_SETCHECK, check, 0)
Button_GetState = lambda hwndCtl:            user32.SendMessageW(hwndCtl, BM_GETSTATE, 0, 0)
Button_SetState = lambda hwndCtl, state:     user32.SendMessageW(hwndCtl, BM_SETSTATE, state, 0)
Button_SetStyle = lambda hwndCtl, style, fRedraw: user32.SendMessageW(hwndCtl, BM_SETSTYLE, style, MAKELPARAM(fRedraw, 0))


########################################
# Button Control Structures
########################################
class BUTTON_IMAGELIST(Structure):
    _fields_ = [
        ("himl", HANDLE),
        ("margin", RECT),
        ("uAlign", UINT),
    ]


########################################
# Wrapper Class
########################################
class Button(Window):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, style=WS_CHILD | WS_VISIBLE, ex_style=0,
            left=0, top=0, width=94, height=23, window_title='OK', wrap_hwnd=None):

        self.__is_checkbox_or_radio = style & BS_TYPEMASK in (BS_CHECKBOX, BS_AUTOCHECKBOX, BS_RADIOBUTTON, BS_AUTORADIOBUTTON)

        super().__init__(
            WC_BUTTON,
            parent_window=parent_window,
            style=style,
            ex_style=ex_style,
            left=left,
            top=top,
            width=width,
            height=height,
            window_title='' if self.__is_checkbox_or_radio else window_title,
            wrap_hwnd=wrap_hwnd
            )

        if self.__is_checkbox_or_radio:
#            self.hide_focus_rects()
            self.checkbox_static = Static(
                self,
                style=WS_CHILD | SS_SIMPLE | WS_VISIBLE,
                left=16,
                top=3,
                width=width - 16,
                height=height - 7,
                window_title=window_title.replace('&', '')
            )
#            self.checkbox_static.show_focus_rects()

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.is_dark:
            if self.__is_checkbox_or_radio:
                self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
            else:
                self.parent_window.unregister_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)
        super().destroy_window()

    ########################################
    #
    ########################################
    def set_font(self, *args, **kwargs):
        if self.__is_checkbox_or_radio:
            self.checkbox_static.set_font(*args, **kwargs)
        else:
            super().set_font(**kwargs)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
        if self.__is_checkbox_or_radio:
            if is_dark:
                self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
            else:
                self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        else:
            if is_dark:
                self.parent_window.register_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)
            else:
                self.parent_window.unregister_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORBTN(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetDCBrushColor(wparam, BG_COLOR_DARK)
            return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            #gdi32.SetBkMode(wparam, TRANSPARENT)
#            gdi32.SetBkColor(wparam, BG_COLOR_DARK) # if self.is_dark else user32.GetSysColor(COLOR_3DFACE))
            #gdi32.SetTextColor(wparam, TEXT_COLOR_DARK) # if self.is_dark else COLOR_WINDOWTEXT)
            return BG_BRUSH_DARK  #gdi32.GetStockObject(DC_BRUSH)
