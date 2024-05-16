import io
import locale
import msvcrt
import os
import re
import signal
import socket
import subprocess
import sys
import time
import traceback

from winapp.mainwin import *
from winapp.dlls import *
from winapp.trayicon import *
from winapp.controls.button import *
from winapp.controls.listbox import *
from winapp.const import *

from const import *

LANG = locale.windows_locale[kernel32.GetUserDefaultUILanguage()]
if not os.path.isdir(os.path.join(APP_DIR, 'resources', 'locale', LANG)):
    LANG = 'en_US'
LANG_DIR = os.path.join(APP_DIR, 'resources', 'locale', LANG)
with open(os.path.join(LANG_DIR, 'strings.pson'), 'rb') as f:
    __ = eval(f.read())
def _(s):
    return __[s] if s in __ else s

IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
IS_CONSOLE = kernel32.GetStdHandle(STD_OUTPUT_HANDLE) != 0


class App(MainWin):

    def __init__(self):

        self._con_counter = CON_ID_START
        self._current_connections = {}
        self._reconnects = {}
        self._hmenu_popup = None
        self._debug = ''

        ########################################
        # create main window
        ########################################
        if IS_FROZEN:
            hicon = user32.LoadIconW(kernel32.GetModuleHandleW(None), MAKEINTRESOURCEW(IDI_APPICON))
        else:
            hicon = user32.LoadImageW(0, os.path.join(APP_DIR, 'app.ico'), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

        super().__init__(
                _('Edit Connections'),
                window_class=APP_CLASS,
                width=480, height=480,
                hicon=hicon,
                hbrush = COLOR_3DFACE + 1
                )

        self.trayicon = TrayIcon(self, self.hicon, APP_NAME, MSG_TRAYICON, show=False)

        connection_list, use_dark, has_autorun = self.load_connections()
        self.connection_dict = {}
        for row in connection_list:
            con_id = self._new_con_id()
            self.connection_dict[con_id] = row

        self.create_popup_menu()
        self.create_ui()
        self.create_dialogs()
        if not IS_CONSOLE:
            self.create_console()

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self.listbox.set_window_pos(
                    width=width - BUTTON_WIDTH - 3 * MARGIN,
                    height=height - 2 * MARGIN,
                    flags=SWP_NOMOVE | SWP_NOACTIVATE | SWP_NOZORDER
                    )
            self.button_add.set_window_pos(
                    x=width - BUTTON_WIDTH - MARGIN,
                    y=20,
                    flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                    )
            self.button_edit.set_window_pos(
                    x=width - BUTTON_WIDTH - MARGIN,
                    y=55,
                    flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                    )
            self.button_delete.set_window_pos(
                    x=width - BUTTON_WIDTH - MARGIN,
                    y=90,
                    flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                    )
            self.button_dark.set_window_pos(
                    x=width - BUTTON_WIDTH - MARGIN,
                    y=height - 2 * MARGIN - 12,
                    flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                    )
            if not IS_CONSOLE:
                self.button_console.set_window_pos(
                        x=width - BUTTON_WIDTH - MARGIN,
                        y=height - 2 * MARGIN - (60 if IS_FROZEN else 36),
                        flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                        )
            if IS_FROZEN:
                self.button_autorun.set_window_pos(
                        x=width - BUTTON_WIDTH - MARGIN,
                        y=height - 2 * MARGIN - 36,
                        flags=SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOZORDER
                        )
        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

        ########################################
        #
        ########################################
        def _on_WM_GETMINMAXINFO(hwnd, wparam, lparam):
            mmi = cast(lparam, LPMINMAXINFO).contents
            mmi.ptMinTrackSize.x = mmi.ptMinTrackSize.y = 320
            return 0

        self.register_message_callback(WM_GETMINMAXINFO, _on_WM_GETMINMAXINFO)

        ########################################
        #
        ########################################
        def _on_WM_CLOSE(hwnd, wparam, lparam):
            self.show(SW_HIDE)
            return TRUE

        self.register_message_callback(WM_CLOSE, _on_WM_CLOSE, True)

        ########################################
        #
        ########################################
        def _on_MSG_TRAYICON(hwnd, wparam, lparam):
            if lparam == WM_LBUTTONDBLCLK:  # WM_LBUTTONUP
                self.show_centered()
                self.set_foreground_window()
            elif lparam == WM_RBUTTONUP:
                pt = POINT()
                user32.GetCursorPos(byref(pt))
                self.set_foreground_window()
                item_id = user32.TrackPopupMenuEx(self._hmenu_popup, TPM_LEFTBUTTON | TPM_RETURNCMD, pt.x, pt.y, self.hwnd, 0)
                user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)
                if item_id == IDM_SETTINGS:
                    self.show_centered()
                elif item_id == IDM_QUIT:
                    self.quit()
                elif item_id >= CON_ID_START:
                    if item_id in self._current_connections:
                        self.disconnect(item_id)
                    else:
                        self.connect(item_id)

        self.register_message_callback(MSG_TRAYICON, _on_MSG_TRAYICON)

        ########################################
        #
        ########################################
        def _on_WM_COMMAND(hwnd, wparam, lparam):
            command = HIWORD(wparam)

            if lparam == self.listbox.hwnd:
                if command == LBN_SELCHANGE:
                    idx = user32.SendMessageW(self.listbox.hwnd, LB_GETCURSEL, 0, 0)
                    self.button_edit.enable_window(int(idx != LB_ERR))
                    self.button_delete.enable_window(int(idx != LB_ERR))
                elif command == LBN_DBLCLK:
                    self.edit_connection()

            elif lparam == self.button_add.hwnd:
                if command == BN_CLICKED:
                    self.add_connection()

            elif lparam == self.button_edit.hwnd:
                if command == BN_CLICKED:
                    self.edit_connection()

            elif lparam == self.button_delete.hwnd:
                if command == BN_CLICKED:
                    self.delete_connection()

            elif lparam == self.button_dark.hwnd:
                if command == BN_CLICKED:
                    self.apply_theme(not self.is_dark)
                    hkey = HKEY()
                    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\{APP_NAME}' , byref(hkey)) == ERROR_SUCCESS:
                        dwsize = sizeof(DWORD)
                        advapi32.RegSetValueExW(hkey, 'dark', 0, REG_DWORD, byref(DWORD(int(self.is_dark))), sizeof(DWORD))
                        advapi32.RegCloseKey(hkey)

            elif IS_FROZEN and lparam == self.button_autorun.hwnd:
                if command == BN_CLICKED:
                    is_checked = user32.SendMessageW(self.button_autorun.hwnd, BM_GETCHECK, 0, 0) == BST_CHECKED
                    hkey = HKEY()
                    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\Microsoft\\Windows\\CurrentVersion\\Run', byref(hkey)) == ERROR_SUCCESS:
                        if is_checked:
                            exe_path = os.path.realpath(os.path.join(APP_DIR, '..', APP_NAME + '.exe'))
                            buf = create_unicode_buffer(f'"{exe_path}" -autorun')
                            advapi32.RegSetValueExW(hkey, APP_NAME, 0, REG_SZ, buf, sizeof(buf))
                        else:
                            advapi32.RegDeleteValueW(hkey, APP_NAME)
                    advapi32.RegCloseKey(hkey)

            elif not IS_CONSOLE and lparam == self.button_console.hwnd:
                if command == BN_CLICKED:
                    is_checked = user32.SendMessageW(self.button_console.hwnd, BM_GETCHECK, 0, 0) == BST_CHECKED
                    user32.ShowWindow(self.hwnd_console, SW_SHOW if is_checked else SW_HIDE)
                    self._debug = '-odebug -ologlevel=debug1' if is_checked else ''

            return FALSE
        self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)

        ########################################
        #
        ########################################
        def _on_poll():
            for con_id in list(self._current_connections.keys()):
                proc = self._current_connections[con_id]
                exit_code = proc.poll()
                if exit_code is not None:
                    #print('Process ended', exit_code)
                    user32.CheckMenuItem(self._hmenu_popup, con_id, MF_BYCOMMAND | MF_UNCHECKED)

                    del self._current_connections[con_id]
                    con = self.connection_dict[con_id]

                    if con["reconnect"] and self._reconnects[con_id] < MAX_RECONNECTS:
                        #print('Reconnecting...', self._reconnects[con_id])
                        self.connect(con_id, True)
                    else:
                        self.set_foreground_window()
                        self.show_message_box(_("Connection '{}' was disconnected.").format(con["name"]),
                                _('Connection lost'), MB_ICONWARNING | MB_OK)

        self.timer_id_poll = self.create_timer(_on_poll, POLL_PERIOD_MS)

        if has_autorun:
            user32.SendMessageW(self.button_autorun.hwnd, BM_SETCHECK, BST_CHECKED, 0)

        if use_dark:
            self.apply_theme(True)
            user32.SendMessageW(self.button_dark.hwnd, BM_SETCHECK, BST_CHECKED, 0)

        self.trayicon.show()

        if len(connection_list) == 0:
            if not '-autorun' in args:
                self.show_centered()
        else:
            for con_id, con in self.connection_dict.items():
                if con["auto"]:
                    self.connect(con_id)

    ########################################
    #
    ########################################
    def load_connections(self):
        connections, use_dark, has_autorun = [], True, False
        data_int = (BYTE * sizeof(DWORD))()
        cbData = DWORD(sizeof(data_int))
        hkey = HKEY()

        if IS_FROZEN and advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\Microsoft\\Windows\\CurrentVersion\\Run', byref(hkey)) == ERROR_SUCCESS:
            has_autorun = advapi32.RegQueryValueExW(hkey, APP_NAME, None, None, None, byref(cbData)) == ERROR_SUCCESS
            advapi32.RegCloseKey(hkey)

        if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\{APP_NAME}', byref(hkey)) != ERROR_SUCCESS:
            advapi32.RegCreateKeyW(HKEY_CURRENT_USER, f'Software\\{APP_NAME}', byref(hkey))
            advapi32.RegCloseKey(hkey)
            return connections, use_dark, has_autorun

        if advapi32.RegQueryValueExW(hkey, 'connections', None, None, None,
                    byref(cbData)) == ERROR_SUCCESS:
            data_str = (BYTE * cbData.value)()
            if advapi32.RegQueryValueExW(hkey, 'connections', None, None, data_str,
                    byref(DWORD(sizeof(data_str)))) == ERROR_SUCCESS:
                connections = eval(cast(data_str, LPWSTR).value)
            if advapi32.RegQueryValueExW(hkey, 'dark', None, None, byref(data_int), byref(cbData)) == ERROR_SUCCESS:
                use_dark = cast(data_int, POINTER(DWORD)).contents.value == 1
        advapi32.RegCloseKey(hkey)

        return connections, use_dark, has_autorun

    ########################################
    #
    ########################################
    def save_connections(self, connection_list):
        hkey = HKEY()
        if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, f'Software\\{APP_NAME}', byref(hkey)) != ERROR_SUCCESS:
            advapi32.RegCreateKeyW(HKEY_CURRENT_USER, f'Software\\{APP_NAME}', byref(hkey))
        buf = create_unicode_buffer(str(connection_list))
        advapi32.RegSetValueExW(hkey, 'connections', 0, REG_SZ, buf, sizeof(buf))
        advapi32.RegCloseKey(hkey)
        return True

    ########################################
    #
    ########################################
    def show_centered(self):
        sw, sh = user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)
        rc = self.get_window_rect()
        w, h = rc.right - rc.left, rc.bottom - rc.top
        self.move_window((sw - w) // 2, (sh - h) // 2, w, h, FALSE)
        self.show()

    ########################################
    #
    ########################################
    def create_ui(self):
        self.listbox = ListBox(
                self,
                style=WS_TABSTOP | WS_CHILD | WS_VISIBLE | LBS_STANDARD | LBS_NOINTEGRALHEIGHT,
                left=MARGIN, top=MARGIN,
                )
        self.listbox.set_font('Segoe UI', 10)
        for con_id, con in self.connection_dict.items():
            pos = self.listbox.add_string(con["name"])
            self.listbox.set_item_data(pos, con_id)
        self.button_add = Button(
            self,
            style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
            window_title=_("Add Connection"))
        self.button_add.set_font()  # 'Segoe UI', 9
        self.button_edit = Button(
            self,
            style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
            window_title=_("Edit Connection"))
        self.button_edit.set_font()
        self.button_edit.enable_window(0)
        self.button_delete = Button(
            self,
            style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
            window_title=_("Delete Connection"))
        self.button_delete.set_font()
        self.button_delete.enable_window(0)
        self.button_dark = Button(
            self,
            style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX,
            width=BUTTON_WIDTH, height=20,
            window_title=_("Use Dark Mode"))
        self.button_dark.set_font()
        if not IS_CONSOLE:
            self.button_console = Button(
                self,
                style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX,
                width=BUTTON_WIDTH, height=20,
                window_title=_("Debug Console"))
            self.button_console.set_font()
        if IS_FROZEN:
            self.button_autorun = Button(
                self,
                style=WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX,
                width=BUTTON_WIDTH, height=20,
                window_title=_("Autorun (Current User)"))
            self.button_autorun.set_font()
        self.hide_focus_rects()

    ########################################
    #
    ########################################
    def create_popup_menu(self):
        if self._hmenu_popup:
            user32.DestroyMenu(self._hmenu_popup)
        menu_data = {"items": []}

        for con_id, row in sorted(self.connection_dict.items(), key=lambda x: x[1]['name']):
            menu_data["items"].append({
                "caption": row["name"],
                "id": con_id,
                "flags": "CHECKED" if con_id in self._current_connections else "",
            })

        menu_data["items"].append({
            "caption": "-"
        })
        menu_data["items"].append({
            "caption": _("Edit Connections") + "...",
            "id": IDM_SETTINGS
        })
        menu_data["items"].append({
            "caption": "-"
        })
        menu_data["items"].append({
            "caption": _("Exit"),
            "id": IDM_QUIT
        })
        self._hmenu_popup = self.make_popup_menu(menu_data)

    ########################################
    #
    ########################################
    def create_dialogs(self):

        class ctx():
            con_id = None

        with open(os.path.join(LANG_DIR, 'dialog_connection.pson'), 'r') as f:
            dialog_dict = eval(f.read())
        def _dialog_proc_connection(hwnd, msg, wparam, lparam):

            def _get_control_text(control_id):
                hwnd_edit = user32.GetDlgItem(hwnd, control_id)
                text_len = user32.GetWindowTextLengthW(hwnd_edit)
                buf = create_unicode_buffer(text_len + 1)
                user32.GetWindowTextW(hwnd_edit, buf, text_len + 1)
                return buf.value

            if msg == WM_INITDIALOG:
                hwnd_combo_letter = user32.GetDlgItem(hwnd, IDC_COMBO_LETTER)
                user32.SendMessageW(hwnd_combo_letter, CB_ADDSTRING, 0, create_unicode_buffer('Auto'))
                for i in range(67, 91): # 67 - 90
                    user32.SendMessageW(hwnd_combo_letter, CB_ADDSTRING, 0, create_unicode_buffer(chr(i)))

                hwnd_combo_auth = user32.GetDlgItem(hwnd, IDC_COMBO_AUTH)
                user32.SendMessageW(hwnd_combo_auth, CB_ADDSTRING, 0, create_unicode_buffer(_('Private Key File')))
                user32.SendMessageW(hwnd_combo_auth, CB_ADDSTRING, 0, create_unicode_buffer(_('Password (saved)')))
                user32.SendMessageW(hwnd_combo_auth, CB_ADDSTRING, 0, create_unicode_buffer(_('Password (ask on connect)')))

                ctx.con_id = lparam
                if ctx.con_id == 0:  # new connection
                    user32.SendMessageW(hwnd_combo_letter, CB_SETCURSEL, 0, 0)
                    user32.SendMessageW(hwnd_combo_auth, CB_SETCURSEL, 0, 0)
                    user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_PORT), create_unicode_buffer('22'))
                    user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_PATH), create_unicode_buffer('/'))
                    user_ssh_dir = os.path.join(os.environ['USERPROFILE'], '.ssh')
                    if os.path.isdir(user_ssh_dir):
                        user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_KEY),
                                create_unicode_buffer(os.path.join(user_ssh_dir, 'id_rsa')))
                    return FALSE

                con = self.connection_dict[lparam]

                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_NAME), create_unicode_buffer(con["name"]))
                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_HOST), create_unicode_buffer(con["host"]))
                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_PORT), create_unicode_buffer(str(con["port"])))
                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_USER), create_unicode_buffer(con["user"]))
                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_PATH), create_unicode_buffer(con["path"]))

                hwnd_static_password = user32.GetDlgItem(hwnd, IDC_STATIC_PASSWORD)
                hwnd_edit_password = user32.GetDlgItem(hwnd, IDC_EDIT_PASSWORD)
                if con["auth"] == "password":
                    pw = self._xor(bytes.fromhex(con['password'])).decode()
                    user32.SetWindowTextW(hwnd_edit_password, create_unicode_buffer(pw))
                user32.ShowWindow(hwnd_static_password, int(con["auth"] == "password"))
                user32.ShowWindow(hwnd_edit_password, int(con["auth"] == "password"))

                hwnd_edit_key = user32.GetDlgItem(hwnd, IDC_EDIT_KEY)
                if con["auth"] == "key":
                    user32.SendMessageW(hwnd_edit_key, WM_SETTEXT, 0, create_unicode_buffer(con["key_file"].replace('/', '\\')))
                user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_STATIC_KEY), int(con["auth"] == "key"))
                user32.ShowWindow(hwnd_edit_key, int(con["auth"] == "key"))
                user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_SELECT_KEY), int(con["auth"] == "key"))

                user32.SendMessageW(hwnd_combo_letter, CB_SETCURSEL, 0 if con["letter"] is None else ord(con["letter"]) - 66, 0)
                user32.SendMessageW(hwnd_combo_auth, CB_SETCURSEL, ["key", "password", "ask_password"].index(con["auth"]), 0)

                user32.SendMessageW(user32.GetDlgItem(hwnd, IDC_CHECK_AUTOCONNECT), BM_SETCHECK, BST_CHECKED if con["auto"] else BST_UNCHECKED, 0)
                user32.SendMessageW(user32.GetDlgItem(hwnd, IDC_CHECK_RECONNECT), BM_SETCHECK, BST_CHECKED if con["reconnect"] else BST_UNCHECKED, 0)

            elif msg == WM_COMMAND:
                control_id = LOWORD(wparam)
                command = HIWORD(wparam)
                if command == CBN_SELCHANGE:
                    if control_id == IDC_COMBO_AUTH:
                        hwnd_combo_auth = user32.GetDlgItem(hwnd, IDC_COMBO_AUTH)
                        idx = user32.SendMessageW(hwnd_combo_auth, CB_GETCURSEL, 0, 0)

                        # "key", "password", "ask_password"
                        user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_STATIC_PASSWORD), int(idx == 1))
                        user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_EDIT_PASSWORD), int(idx == 1))

                        user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_STATIC_KEY), int(idx == 0))
                        user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_EDIT_KEY), int(idx == 0))
                        user32.ShowWindow(user32.GetDlgItem(hwnd, IDC_SELECT_KEY), int(idx == 0))

                        if idx == 0 and _get_control_text(IDC_EDIT_KEY) == '':
                            user_ssh_dir = os.path.join(os.environ['USERPROFILE'], '.ssh')
                            if os.path.isdir(user_ssh_dir):
                                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_KEY),
                                        create_unicode_buffer(os.path.join(user_ssh_dir, 'id_rsa')))

                elif command == BN_CLICKED:

                    if control_id == IDC_SELECT_KEY:
                            fn = self.get_open_filename(_('Select Private Key'),
                                    initial_dir=os.path.join(os.environ['USERPROFILE'], '.ssh'))
                            if fn:
                                user32.SetWindowTextW(user32.GetDlgItem(hwnd, IDC_EDIT_KEY), create_unicode_buffer(fn))

                    elif control_id == IDC_OK:
                        con = {}
                        con["name"] = _get_control_text(IDC_EDIT_NAME)
                        con["host"] = _get_control_text(IDC_EDIT_HOST)
                        con["port"] = _get_control_text(IDC_EDIT_PORT)
                        con["user"] = _get_control_text(IDC_EDIT_USER)
                        con["path"] = _get_control_text(IDC_EDIT_PATH)

                        for v in con.values():
                            if v == '':
                                self.show_message_box(
                                    _('Please fill out all fields.'),
                                    _('Settings incomplete'),
                                    MB_ICONERROR | MB_OK)
                                return FALSE

                        # if a new connection, make sure that name is unique
                        if ctx.con_id is None and con["name"] in [con["name"] for con in self.connection_dict.values()]:
                            self.show_message_box(
                                    _('Please select a unique connection name.'),
                                    _('Name already used'),
                                    MB_ICONERROR | MB_OK)
                            return FALSE

                        hwnd_combo_letter = user32.GetDlgItem(hwnd, IDC_COMBO_LETTER)
                        idx = user32.SendMessageW(hwnd_combo_letter, CB_GETCURSEL, 0, 0)
                        con["letter"] = None if idx == 0 else chr(66 + idx)

                        hwnd_combo_auth = user32.GetDlgItem(hwnd, IDC_COMBO_AUTH)
                        idx = user32.SendMessageW(hwnd_combo_auth, CB_GETCURSEL, 0, 0)
                        con["auth"] = ["key", "password", "ask_password"][idx]

                        if con["auth"] == 'key':
                            fn = _get_control_text(IDC_EDIT_KEY)
                            if fn == '':
                                self.show_message_box(
                                    _('Please select a private key file.'),
                                    _('Key missing'),
                                    MB_ICONERROR | MB_OK)
                                return FALSE
                            elif not os.path.isfile(fn):
                                self.show_message_box(
                                    _('Please select an existing private key file.'),
                                    _('Key doesn\'t exist'),
                                    MB_ICONERROR | MB_OK)
                                return FALSE
                            con["key_file"] = fn
                        elif con["auth"] == 'password':
                            pw = _get_control_text(IDC_EDIT_PASSWORD)
                            if pw == '':
                                self.show_message_box(
                                    _('Please enter a password.'),
                                    _('Password missing'),
                                    MB_ICONERROR | MB_OK)
                                return FALSE
                            con["password"] = self._xor(pw.encode()).hex()


                        con["auto"] = user32.SendMessageW(user32.GetDlgItem(hwnd, IDC_CHECK_AUTOCONNECT), BM_GETCHECK, 0, 0) == BST_CHECKED
                        con["reconnect"] = user32.SendMessageW(user32.GetDlgItem(hwnd, IDC_CHECK_RECONNECT), BM_GETCHECK, 0, 0) == BST_CHECKED

                        if ctx.con_id:
                            con_id = ctx.con_id
                            idx = user32.SendMessageW(self.listbox.hwnd, LB_GETCURSEL, 0, 0)
                            user32.SendMessageW(self.listbox.hwnd, LB_DELETESTRING, idx, 0)
                        else:
                            con_id = self._new_con_id()

                        self.connection_dict[con_id] = con

                        idx = self.listbox.add_string(con["name"])
                        self.listbox.set_item_data(idx, con_id)
                        user32.SendMessageW(self.listbox.hwnd, LB_SETCURSEL, idx, 0)

                        self.save_connections(list(self.connection_dict.values()))
                        self.create_popup_menu()

                        user32.EndDialog(hwnd, 1)

                    elif control_id == IDC_CANCEL:
                        user32.EndDialog(hwnd, 0)

            return FALSE
        self.dialog_connection = Dialog(self, dialog_dict, _dialog_proc_connection)

    ########################################
    #
    ########################################
    def create_console(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        proc = subprocess.Popen(
            #f'cmd.exe /k title {_("Debug Console")}',

            os.path.join(BIN_DIR, 'bash.exe'),
            env = {'PATH': BIN_DIR},

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo
        )

        for i in range(50):
            time.sleep(.05)
            if kernel32.AttachConsole(proc.pid):
                break

        kernel32.SetConsoleTitleW( _("Debug Console"))
        self.hwnd_console = kernel32.GetConsoleWindow()

        # deactivate console's close button
        hmenu = user32.GetSystemMenu(self.hwnd_console, FALSE)
        if hmenu:
            user32.DeleteMenu(hmenu, SC_CLOSE, MF_BYCOMMAND)

    	# redirect unbuffered STDOUT to the console
        lStdOutHandle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdOutHandle, os.O_TEXT)
        sys.stdout = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through=True)

        # redirect unbuffered STDERR to the console
        lStdErrHandle = kernel32.GetStdHandle(STD_ERROR_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdErrHandle, os.O_TEXT)
        sys.stderr = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through=True)

    	# redirect unbuffered STDIN to the console
        lStdInHandle = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdInHandle, os.O_TEXT)
        sys.stdin = io.TextIOWrapper(os.fdopen(hConHandle, 'rb', 0), write_through=True)


    ########################################
    #
    ########################################
    def _check_is_open(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((host, int(port)))
            s.shutdown(2)
            return True
        except:
            return False

    ########################################
    #
    ########################################
    def connect(self, con_id, is_reconnect=False):  #open_explorer=True):
        con = self.connection_dict[con_id]

        # first check if host and ip are accessible at all
        if not is_reconnect and not self._check_is_open(con['host'], con['port']):
            self.show_message_box(_("{}:{} can\'t be reached.").format(con["host"], con["port"]),
                    _('No connection possible'), MB_ICONERROR | MB_OK)
            return

        bash = os.path.join(BIN_DIR, 'bash.exe')

        if con["letter"]:
            if self._drive_letter_in_use(con["letter"]):
                res = self.show_message_box(
                        _('Drive letter {} is already in use.\n\n'
                          'Do you want to use the first free letter instead?')
                          .format(con["letter"]),
                        _('Drive letter in use'),
                        MB_ICONQUESTION | MB_YESNO)
                if res != IDYES:
                    if is_reconnect:
                        del self._current_connections[con_id]
                    return
                letter = self._find_free_drive_letter()
            else:
                letter = con["letter"]
        else:
            letter = self._find_free_drive_letter()

        env = {'PATH': BIN_DIR}
        volname = re.sub(r'[<>:"/\\|?*]', '_', con['name'][:32])
        command = ("sshfs {user}@{host}:{path} {use_letter}: -p{port} -ovolname='{volname}' -f {debug} "
            "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oidmap=user -ouid=-1 "
            "-ogid=-1 -oumask=000 -ocreate_umask=000 -omax_readahead=1GB "
            "-oallow_other -olarge_read -okernel_cache -ofollow_symlinks -oConnectTimeout={connect_timeout}"
            .format(**{'volname': volname, 'use_letter': letter, 'connect_timeout': SSH_CONNECT_TIMEOUT_SEC,
                    'debug': self._debug}, **con))

        if con["auth"] == "key":
            command += " -oPreferredAuthentications=publickey -oIdentityFile='{}'".format(con['key_file'].replace('\\', '/'))
            self._current_connections[con_id] = subprocess.Popen(
                    f'"{bash}" -c "{command}"',
                    env = env,
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
                    )
        else:
            if con["auth"] == "ask_password":
                pw = self.show_prompt(text=_('Password for {}:').format(con['name']),
                        caption=_('Enter Password'), is_password=True, dialog_width=200)
                if not pw:
                    return
            else:
                pw = self._xor(bytes.fromhex(con['password'])).decode()
            command += " -opassword_stdin"
            self._current_connections[con_id] = subprocess.Popen(
                    f'"{bash}" -c "{command}"',
                    env = env,
                    stdin = subprocess.PIPE,
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP,
                    )
            try:
                self._current_connections[con_id].communicate(pw.encode() + b'\n', timeout=0)
            except:
                pass

        self._reconnects[con_id] = self._reconnects[con_id] + 1 if is_reconnect else 0

        user32.CheckMenuItem(self._hmenu_popup, con_id, MF_BYCOMMAND | MF_CHECKED)
        if not is_reconnect:
            for i in range(10):
                time.sleep(.5)
                if os.path.isdir(f'{letter}:/'):
                    os.system(f'C:\\Windows\\explorer.exe {letter}:\\')
                    break

    ########################################
    #
    ########################################
    def disconnect(self, con_id):
        if con_id in self._current_connections:
            proc = self._current_connections[con_id]
            del self._current_connections[con_id]
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        user32.CheckMenuItem(self._hmenu_popup, con_id, MF_BYCOMMAND | MF_UNCHECKED)

    ########################################
    #
    ########################################
    def add_connection(self):
        self.dialog_show_sync(self.dialog_connection, 0)

    ########################################
    #
    ########################################
    def edit_connection(self):
        idx = user32.SendMessageW(self.listbox.hwnd, LB_GETCURSEL, 0, 0)
        con_id = user32.SendMessageW(self.listbox.hwnd, LB_GETITEMDATA, idx, 0)
        self.dialog_show_sync(self.dialog_connection, con_id)

    ########################################
    #
    ########################################
    def delete_connection(self):
        idx = user32.SendMessageW(self.listbox.hwnd, LB_GETCURSEL, 0, 0)
        con_id = user32.SendMessageW(self.listbox.hwnd, LB_GETITEMDATA, idx, 0)
        user32.SendMessageW(self.listbox.hwnd, LB_DELETESTRING, idx, 0)
        self.button_edit.enable_window(0)
        self.button_delete.enable_window(0)
        del self.connection_dict[con_id]
        self.save_connections(list(self.connection_dict.values()))
        self.create_popup_menu()

    ########################################
    #
    ########################################
    def quit(self):
        cnt = len(self._current_connections)
        if cnt:
            if cnt > 1:
                res = self.show_message_box(
                        _('{} processes are still running.\n\nDo you want to quit them?').format(cnt),
                        _('SSHFS processes running'),
                        MB_ICONQUESTION | MB_YESNOCANCEL)
            else:
                res = self.show_message_box(
                        _('A process is still running.\n\nDo you want to quit it?'),
                        _('SSHFS process running'),
                        MB_ICONQUESTION | MB_YESNOCANCEL)
            if res == IDCANCEL:
                return
            elif res == IDYES:
                for con_id in list(self._current_connections.keys()):
                    self.disconnect(con_id)
        super().quit()

    ########################################
    #
    ########################################
    def _new_con_id(self):
        con_id = self._con_counter
        self._con_counter += 1
        return con_id

    ########################################
    # find first free drive letter
    ########################################
    def _find_free_drive_letter(self):
        command = '@echo off&for %a in (Z Y X W V U T S R Q P O N M L K J I H G F E D C) do if not exist %a:\\ echo %a'
        res = subprocess.run(command, shell=True, capture_output=True)
        return res.stdout.decode('windows-1252').split()[-1]

    ########################################
    # is this problematic?
    ########################################
    def _drive_letter_in_use(self, letter):
        return os.path.isdir(f'{letter}:/')

    ########################################
    #
    ########################################
    def _xor(self, message):
        return bytes(a ^ b for a, b in zip(message, MASTER_KEY))


########################################
#
########################################
if __name__ == "__main__":
    sys.excepthook = traceback.print_exception
    # force single instance
    if user32.FindWindowW(APP_CLASS, NULL):
        sys.exit(1)
    sys.exit(App().run())
