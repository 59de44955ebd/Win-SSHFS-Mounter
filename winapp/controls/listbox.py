# https://learn.microsoft.com/en-us/windows/win32/controls/list-boxes

from winapp.const import *
from winapp.window import *


########################################
# Wrapper Class
########################################
class ListBox(Window):

    ########################################
    #
    ########################################
    def __init__(self, parent_window=None, style=WS_CHILD | WS_VISIBLE, ex_style=0,
            left=0, top=0, width=0, height=0, window_title=None, wrap_hwnd=None):

        super().__init__(
            WC_LISTBOX,
            parent_window=parent_window,
            style=style,
            left=left,
            top=top,
            width=width,
            height=height,
            window_title=window_title,
            wrap_hwnd=wrap_hwnd
            )

        def _on_WM_NCPAINT(hwnd, wparam, lparam):
            hdc = user32.GetDC(hwnd)
            #hdc = user32.GetDCEx(hwnd, wparam, DCX_WINDOW | DCX_INTERSECTRGN)  # returns None
            rc = self.get_client_rect()
            user32.InflateRect(byref(rc), 1, 1)
            user32.FrameRect(hdc, byref(rc), gdi32.CreateSolidBrush(0x646464))
            user32.ReleaseDC(hwnd, hdc)
            return 0

        self.register_message_callback(WM_NCPAINT, _on_WM_NCPAINT)

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.is_dark:
            self.parent_window.unregister_message_callback(WM_CTLCOLORLISTBOX, self.on_WM_CTLCOLORLISTBOX)
        super().destroy_window()

    ########################################
    #
    ########################################
    def add_string(self, s, data=None):
        idx = user32.SendMessageW(self.hwnd, LB_ADDSTRING, 0, s)
        if data:
            user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)
        return idx

    ########################################
    #
    ########################################
    def set_item_data(self, idx, data):
        user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)

    ########################################
    #
    ########################################
    def rename_item(self, idx, new_name):
        data = user32.SendMessageW(self.hwnd, LB_GETITEMDATA, idx, 0)
        user32.SendMessageW(self.hwnd, LB_DELETESTRING, idx, 0)

        #user32.SendMessageW(self.hwnd, LB_INSERTSTRING, idx, new_name)
        idx = user32.SendMessageW(self.hwnd, LB_ADDSTRING, 0, new_name)

        user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)

    ########################################
    #
    ########################################
    def find_item_by_data(self, data):
        cnt = user32.SendMessageW(self.hwnd, LB_GETCOUNT, 0, 0)
        for idx in range(cnt):
            if user32.SendMessageW(self.hwnd, LB_GETITEMDATA, idx, 0) == data:
                return idx

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        #self.is_dark = is_dark

        #uxtheme.SetWindowTheme(self.hwnd, '', '')
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
        #self.hide_focus_rects()
        #uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', 'SysListView32')

        if is_dark:
            self.parent_window.register_message_callback(WM_CTLCOLORLISTBOX, self.on_WM_CTLCOLORLISTBOX)
        else:
            self.parent_window.unregister_message_callback(WM_CTLCOLORLISTBOX, self.on_WM_CTLCOLORLISTBOX)

    ########################################
    #
    ########################################
    def on_WM_CTLCOLORLISTBOX(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetTextColor(wparam, TEXT_COLOR_DARK)
#            gdi32.SetBkColor(wparam, 0x2b2b2b)  #sCONTROL_BG_COLOR_DARK)
            gdi32.SetDCBrushColor(wparam, CONTROL_BG_COLOR_DARKER)
            return gdi32.GetStockObject(DC_BRUSH)
