# https://learn.microsoft.com/en-us/windows/win32/controls/static-controls

from winapp.const import *
from winapp.window import *
from winapp.dlls import user32
from winapp.themes import *


########################################
# Wrapper Class
########################################
class Static(Window):

    ########################################
    #
    ########################################
    def __init__(self, parent_window=None, style=WS_CHILD | WS_VISIBLE, ex_style=0,
            left=0, top=0, width=0, height=0, window_title=0,
            bg_color=COLOR_WINDOW + 1,
            bg_color_dark=BG_COLOR_DARK,
            wrap_hwnd=None
            ):

        self.bg_color = bg_color
        self.bg_color_dark = bg_color_dark

        super().__init__(
            WC_STATIC,
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

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.is_dark:
            self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        super().destroy_window()

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetTextColor(wparam, TEXT_COLOR_DARK)
            gdi32.SetBkColor(wparam, BG_COLOR_DARK)
            gdi32.SetDCBrushColor(wparam, BG_COLOR_DARK)
            return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    #
    ########################################
    def set_image(self, hbitmap):
        user32.SendMessageW(self.hwnd, STM_SETIMAGE, IMAGE_BITMAP, hbitmap)

    ########################################
    #
    ########################################
    def set_icon(self, hicon):
        user32.SendMessageW(self.hwnd, STM_SETICON, hicon, 0)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        else:
            self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        self.force_redraw_window()  # triggers WM_CTLCOLORSTATIC
