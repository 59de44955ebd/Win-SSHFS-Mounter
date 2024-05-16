# https://learn.microsoft.com/en-us/windows/win32/controls/combo-boxes

from ctypes import Structure, sizeof, byref
from ctypes.wintypes import DWORD, RECT, HWND
from winapp.const import *
from winapp.window import Window
from winapp.dlls import gdi32, user32, uxtheme
from winapp.themes import TEXT_COLOR_DARK, CONTROL_BG_COLOR_DARK


class COMBOBOXINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(COMBOBOXINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
            ("cbSize", DWORD),
            ("rcItem", RECT),
            ("rcButton", RECT),
            ("stateButton", DWORD),
            ("hwndCombo", HWND),
            ("hwndItem", HWND),
            ("hwndList", HWND),
            ]


# #######################################
# Wrapper Class
# #######################################
class ComboBox(Window):

    # #######################################
    #
    # #######################################
    def __init__(self, parent_window, style=WS_CHILD | WS_VISIBLE, ex_style=0,
                 left=0, top=0, width=0, height=0, window_title=0,
                 wrap_hwnd=None):

        super().__init__(
                WC_COMBOBOX,
                parent_window=parent_window,
                style=style,
                ex_style=ex_style,
                left=left,
                top=top,
                width=width,
                height=height,
                window_title=window_title,
                wrap_hwnd=wrap_hwnd
                )

        self.__has_edit = style & CBS_DROPDOWN

    # #######################################
    #
    # #######################################
    def destroy_window(self):
        if self.is_dark:
            self.unregister_message_callback(WM_CTLCOLORLISTBOX,
                                             self.on_WM_CTLCOLORLISTBOX)
            if self.__has_edit:
                self.unregister_message_callback(WM_CTLCOLOREDIT,
                                                 self._on_WM_CTLCOLOREDIT)
        super().destroy_window()

    def add_string(self, s):
        user32.SendMessageW(self.hwnd, CB_ADDSTRING, 0, s)

    def set_current_selection(self, idx):
        user32.SendMessageW(self.hwnd, CB_SETCURSEL, idx, 0)

    def get_current_selection(self):
        return user32.SendMessageW(self.hwnd, CB_GETCURSEL, 0, 0)

    # #######################################
    #
    # #######################################
    def apply_theme(self, is_dark):
        self.is_dark = is_dark

        uxtheme.SetWindowTheme(self.hwnd,
                               'DarkMode_CFD' if is_dark else 'CFD', None)

        # scrollbar colors
        ci = COMBOBOXINFO()
        user32.SendMessageW(self.hwnd, CB_GETCOMBOBOXINFO, 0, byref(ci))
        uxtheme.SetWindowTheme(ci.hwndList,
                               'DarkMode_Explorer' if is_dark else 'Explorer',
                               None)

        if is_dark:
            self.register_message_callback(WM_CTLCOLORLISTBOX,
                                           self.on_WM_CTLCOLORLISTBOX)
            if self.__has_edit:
                self.register_message_callback(WM_CTLCOLOREDIT,
                                               self._on_WM_CTLCOLOREDIT)
        else:
            self.unregister_message_callback(WM_CTLCOLORLISTBOX,
                                             self.on_WM_CTLCOLORLISTBOX)
            if self.__has_edit:
                self.unregister_message_callback(WM_CTLCOLOREDIT,
                                                 self._on_WM_CTLCOLOREDIT)

    # #######################################
    #
    # #######################################
    def on_WM_CTLCOLORLISTBOX(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, TEXT_COLOR_DARK)
        gdi32.SetBkColor(wparam, CONTROL_BG_COLOR_DARK)
        gdi32.SetDCBrushColor(wparam, CONTROL_BG_COLOR_DARK)
        return gdi32.GetStockObject(DC_BRUSH)

    # #######################################
    #
    # #######################################
    def _on_WM_CTLCOLOREDIT(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, TEXT_COLOR_DARK)
        gdi32.SetBkColor(wparam, CONTROL_BG_COLOR_DARK)
        gdi32.SetDCBrushColor(wparam, CONTROL_BG_COLOR_DARK)
        return gdi32.GetStockObject(DC_BRUSH)
