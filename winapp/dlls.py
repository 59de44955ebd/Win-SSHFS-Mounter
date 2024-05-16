from ctypes import windll, c_uint, POINTER, c_int, c_void_p, c_wchar_p, Structure
from ctypes.wintypes import *
from winapp.wintypes_extended import WNDPROC, LONG_PTR, ENUMRESNAMEPROCW, ACCEL, FONTENUMPROCW, LOGFONTW

advapi32 = windll.Advapi32
comctl32 = windll.Comctl32
comdlg32 = windll.comdlg32
gdi32 = windll.Gdi32
kernel32 = windll.Kernel32
ole32 = windll.Ole32
shell32 = windll.shell32
shlwapi = windll.Shlwapi
user32 = windll.user32
uxtheme = windll.UxTheme

########################################
# advapi32
########################################
LSTATUS = LONG
PHKEY = POINTER(HKEY)

advapi32.RegOpenKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegOpenKeyW.restype = LSTATUS

advapi32.RegCreateKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegCreateKeyW.restype = LSTATUS

advapi32.RegCloseKey.argtypes = (HKEY, )
advapi32.RegCloseKey.restype = LSTATUS

advapi32.RegDeleteValueW.argtypes = (HKEY, LPCWSTR)
advapi32.RegDeleteValueW.restype = LSTATUS

advapi32.RegQueryValueExW.argtypes = (HKEY, LPCWSTR, POINTER(DWORD), POINTER(DWORD), c_void_p, POINTER(DWORD))
advapi32.RegQueryValueExW.restype = LSTATUS

advapi32.RegSetValueExW.argtypes = (HKEY, LPCWSTR, DWORD, DWORD, c_void_p, DWORD)  # POINTER(BYTE)
advapi32.RegSetValueExW.restype = LSTATUS

########################################
# comctl32
########################################
comctl32.ImageList_Add.argtypes = (HANDLE, HBITMAP, HBITMAP)  # HIMAGELIST

comctl32.ImageList_BeginDrag.argtypes = (HANDLE, INT, INT, INT)
comctl32.ImageList_Create.restype = HANDLE

comctl32.ImageList_Destroy.argtypes = (HANDLE,)

comctl32.ImageList_Draw.argtypes = (HANDLE, INT, HDC, INT, INT, UINT)  # HIMAGELIST

comctl32.ImageList_GetIcon.argtypes = (HANDLE, INT, UINT)
comctl32.ImageList_GetIcon.restype = HICON

comctl32.ImageList_GetIconSize.argtypes = (HANDLE, POINTER(INT), POINTER(INT))  # HIMAGELIST

comctl32.ImageList_GetImageCount.argtypes = (HANDLE, )

comctl32.ImageList_GetImageInfo.argtypes = (HANDLE, INT, LPVOID)  # POINTER(IMAGEINFO)]

comctl32.ImageList_LoadImageW.argtypes = (HINSTANCE, LPCWSTR, INT, INT, COLORREF, UINT, UINT)
comctl32.ImageList_LoadImageW.restype = HANDLE

comctl32.ImageList_Merge.argtypes = (HANDLE, INT, HANDLE, INT, INT, INT)
comctl32.ImageList_Merge.restype = HANDLE

comctl32.ImageList_Remove.argtypes = (HANDLE, INT)

comctl32.ImageList_Replace.argtypes = (HANDLE, INT, HANDLE, HANDLE)

comctl32.ImageList_ReplaceIcon.argtypes = (HANDLE, INT, HICON)

#comctl32.ImageList_AddIcon.argtypes = (HANDLE, HANDLE)
comctl32.ImageList_AddIcon = lambda handle, hicon: comctl32.ImageList_ReplaceIcon(handle, -1, hicon)

########################################
# gdi32
########################################
gdi32.BitBlt.argtypes = (HANDLE, INT, INT, INT, INT, HANDLE, INT, INT, DWORD)

gdi32.CreateBitmap.argtypes = (INT, INT, UINT, UINT, LPVOID)
gdi32.CreateBitmap.restype = HBITMAP

gdi32.CreateBitmapIndirect.restype = HBITMAP

gdi32.CreateCompatibleDC.argtypes = (HANDLE, )
gdi32.CreateCompatibleDC.restype = HANDLE

gdi32.CreateCompatibleBitmap.argtypes = (HANDLE, INT, INT)

gdi32.CreateDIBitmap.argtypes = (HANDLE, c_void_p, DWORD, LPVOID, c_void_p, UINT)
gdi32.CreateDIBitmap.restype = HANDLE

gdi32.CreateFontW.argtypes = (INT, INT, INT, INT, INT, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, LPCWSTR)
gdi32.CreateFontW.restype = HFONT

gdi32.CreateSolidBrush.argtypes = (COLORREF, )
gdi32.CreateSolidBrush.restype = HANDLE

gdi32.DeleteDC.argtypes = (HANDLE, )

gdi32.DeleteObject.argtypes = (HANDLE, )

gdi32.DPtoLP.argtypes = (HDC, POINTER(POINT), INT)

#int EnumFontFamiliesExW(
#  [in] HDC           hdc,
#  [in] LPLOGFONTW    lpLogfont,
#  [in] FONTENUMPROCW lpProc,
#  [in] LPARAM        lParam,
#       DWORD         dwFlags
#);
gdi32.EnumFontFamiliesExW.argtypes = (HDC, POINTER(LOGFONTW), FONTENUMPROCW, LPARAM, DWORD)

gdi32.ExtTextOutW.argtypes = (HANDLE, INT, INT, UINT, POINTER(RECT), LPCWSTR, UINT, POINTER(INT))

gdi32.FillRgn.argtypes = (HDC, HRGN, HBRUSH)

gdi32.GetDIBits.argtypes = (HDC, HBITMAP, UINT, UINT, LPVOID, c_void_p, UINT)
gdi32.GetDIBits.restype = c_int

gdi32.GetDeviceCaps.argtypes = (HDC, INT)

gdi32.GetObjectW.argtypes = (HANDLE, INT, LPVOID)

gdi32.GetTextMetricsW.argtypes = (HANDLE, LPVOID)

gdi32.MaskBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, HBITMAP, INT, INT, DWORD)

gdi32.SelectObject.argtypes = (HANDLE, HANDLE)

gdi32.SetBkColor.argtypes = (HANDLE, COLORREF)

gdi32.SetBkMode.argtypes = (HANDLE, INT)

gdi32.SetDCBrushColor.argtypes = (HANDLE, COLORREF)
gdi32.SetDCPenColor.argtypes = (HANDLE, COLORREF)

gdi32.SetTextColor.argtypes = (HANDLE, COLORREF)

gdi32.SetViewportExtEx.argtypes = (HDC, INT, INT, POINTER(SIZE))

gdi32.SetWindowExtEx.argtypes = (HDC, INT, INT, POINTER(SIZE))

########################################
# kernel32
########################################
kernel32.EnumResourceNamesW.argtypes = (HMODULE, LPCWSTR, ENUMRESNAMEPROCW, LONG_PTR)
kernel32.EnumResourceNamesW.restype = BOOL

kernel32.FindResourceW.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
kernel32.FindResourceW.restype = HANDLE

kernel32.FreeLibrary.argtypes = (HANDLE, )

kernel32.GetModuleHandleW.argtypes = (LPCWSTR,)
kernel32.GetModuleHandleW.restype = HMODULE

kernel32.GetProcessId.argytypes = (HANDLE,)

kernel32.GlobalAlloc.argtypes = (UINT, DWORD)
kernel32.GlobalAlloc.restype = HGLOBAL

kernel32.GlobalLock.argtypes = (HGLOBAL, )
kernel32.GlobalLock.restype = LPVOID

kernel32.GlobalSize.argtypes = (HGLOBAL, )

kernel32.GlobalUnlock.argtypes = (HANDLE,)

kernel32.LoadLibraryW.restype = HANDLE

kernel32.LoadResource.argtypes = (HANDLE, HANDLE)
kernel32.LoadResource.restype = HANDLE

kernel32.LockResource.argtypes = (HANDLE, )
kernel32.LockResource.restype = HANDLE

kernel32.SizeofResource.argtypes = (HANDLE, HANDLE)

########################################
# shell32
########################################
shell32.DragAcceptFiles.argtypes = (HWND, BOOL)

shell32.DragQueryFileW.argtypes = (WPARAM, UINT, LPWSTR, UINT)

shell32.DragFinish.argtypes = (WPARAM, )

shell32.DragQueryPoint.argtypes = (WPARAM, LPPOINT)

shell32.Shell_NotifyIconW.argtypes = (DWORD, LPVOID)

shell32.RunFileDlg = shell32[61]
shell32.RunFileDlg.argtypes = (HWND, HANDLE, LPWSTR, LPWSTR, LPWSTR, UINT)

#HINSTANCE ShellExecuteW(
#  [in, optional] HWND    hwnd,
#  [in, optional] LPCWSTR lpOperation,
#  [in]           LPCWSTR lpFile,
#  [in, optional] LPCWSTR lpParameters,
#  [in, optional] LPCWSTR lpDirectory,
#  [in]           INT     nShowCmd
#);
shell32.ShellExecuteW.argtypes = (HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT)
shell32.ShellExecuteW.restype = HINSTANCE

shell32.SHGetStockIconInfo.argtypes = (UINT, UINT, LPVOID)  # POINTER(SHSTOCKICONINFO)

shell32.SHGetFileInfoW.argtypes = (LPCWSTR, DWORD, LPVOID, UINT, UINT)
shell32.SHGetFileInfoW.restype = POINTER(DWORD) #DWORD_PTR

########################################
# user32
########################################
user32.CreateAcceleratorTableW.argtypes = (POINTER(ACCEL), INT)
user32.CreateAcceleratorTableW.restype = HACCEL

user32.CreateDialogIndirectParamW.argtypes = (HINSTANCE, LPVOID, HWND, WNDPROC, LPARAM)  # LPCDLGTEMPLATEW
user32.CreateDialogIndirectParamW.restype = HWND

user32.DestroyAcceleratorTable.restype = HANDLE
user32.TranslateAcceleratorW.argtypes = (HWND, HANDLE, POINTER(MSG))

user32.CopyImage.argtypes = [HANDLE, UINT, INT, INT, UINT]
user32.CopyImage.restype = HANDLE

user32.CreateIconFromResourceEx.argtypes = (c_void_p, DWORD, BOOL, DWORD, INT, INT, UINT)  # PBYTE
user32.CreateIconFromResourceEx.restype = HICON

user32.CreateIconIndirect.argtypes = (HANDLE, )  # POINTER(ICONINFO)

user32.EnableWindow.argytpes = (HWND, BOOL)

user32.DeleteMenu.argtypes = (HMENU, UINT, UINT)

user32.DestroyWindow.argytpes = (HWND,)

user32.DrawEdge.argtypes = (HDC, POINTER(RECT), UINT, UINT)

user32.DrawFocusRect.argtypes = (HANDLE, POINTER(RECT))

user32.DrawTextW.argtypes = (HANDLE, LPCWSTR, INT, POINTER(RECT), UINT)

user32.FillRect.argtypes = (HANDLE, POINTER(RECT), HBRUSH)

user32.FindWindowW.restype = HWND

user32.FindWindowExW.argtypes = (HWND, HWND, LPCWSTR, LPCWSTR)
user32.FindWindowExW.restype = HWND

user32.FrameRect.argtypes = (HDC, POINTER(RECT), HBRUSH)

user32.GetCapture.restype = HWND

user32.GetCaretPos.argtypes = (POINTER(POINT),)

user32.GetClassNameW.argtypes = (HWND, LPWSTR, INT)

user32.GetClipboardData.restype = HANDLE

user32.GetDC.argtypes = (HANDLE,)
user32.GetDC.restype = HDC

user32.GetDCEx.argtypes = (HWND, HRGN, DWORD)
user32.GetDCEx.restype = HDC

user32.GetDesktopWindow.restype = HANDLE
user32.GetForegroundWindow.restype = HANDLE

user32.GetMenuBarInfo.argtypes = (HWND, LONG, LONG, LPVOID)  # PMENUBARINFO

user32.GetMenuItemInfoW.argtypes = (HMENU, UINT, BOOL, LPVOID)  # LPMENUITEMINFOW

user32.GetMenuStringW.argtypes = (HMENU, UINT, LPWSTR, INT, UINT)

user32.GetWindow.argtypes = (HANDLE, UINT)

user32.GetWindowLongPtrA.argtypes = (HWND, LONG_PTR)
user32.GetWindowLongPtrA.restype = ULONG

user32.GetWindowLongPtrW.argtypes = (HWND, LONG_PTR)
user32.GetWindowLongPtrW.restype = WNDPROC

user32.GetWindowLongW.argtypes = (HWND, INT)
user32.GetWindowLongW.restype = LONG

user32.GetWindowTextW.argtypes = (HWND, LPWSTR, INT)

user32.GetWindowThreadProcessId.argtypes = (HANDLE, POINTER(DWORD))

user32.DefDlgProcW.argtypes = (HWND, c_uint, WPARAM, LPARAM)

user32.DefWindowProcW.argtypes = (HWND, c_uint, WPARAM, LPARAM)

user32.InvalidateRect.argtypes = (HWND, POINTER(RECT), BOOL)

user32.InvertRect.argtypes = (HDC, POINTER(RECT))

user32.IsDialogMessageW.argtypes = (HWND, POINTER(MSG))
user32.IsDialogMessageW.restype = BOOL

user32.IsWindowVisible.argtypes = (HWND, )

user32.LoadIconW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadIconW.restype = HICON

user32.LoadImageW.argtypes = (HINSTANCE, LPCWSTR, UINT, INT, INT, UINT)
user32.LoadImageW.restype = HANDLE

user32.MapDialogRect.argtypes = (HWND, POINTER(RECT))

user32.MapWindowPoints.argtypes = (HWND, HWND, LPVOID, UINT)

user32.MB_GetString.restype = LPCWSTR

user32.OffsetRect.argtypes = (POINTER(RECT), INT, INT)

user32.OpenClipboard.argtypes = (HWND,)

user32.PostMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.PostMessageW.restype = LONG_PTR

user32.ReleaseDC.argtypes = (HWND, HANDLE)

user32.SetClassLongPtrW.argtypes = (HWND, INT, LONG_PTR)

user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.restype = HANDLE

user32.SetMenu.argtypes = (HWND, HMENU)

# LPVOID to allow to send pointers
user32.SendMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.SendMessageW.restype = LONG_PTR

user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.restype = HANDLE

user32.SetSysColors.argtypes = (INT, POINTER(INT), POINTER(COLORREF))

user32.SetWindowLongPtrA.argtypes = (HWND, LONG_PTR, ULONG)
user32.SetWindowLongPtrA.restype = LONG

user32.SetWindowLongPtrW.argtypes = (HWND, LONG_PTR, WNDPROC)
user32.SetWindowLongPtrW.restype = WNDPROC

user32.SetWindowPos.argtypes = (HWND, LONG_PTR, INT, INT, INT, INT, UINT)

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook
# https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants?redirectedfrom=MSDN
user32.SetWinEventHook.restype = HANDLE

user32.TrackPopupMenu.argtypes = (HANDLE, UINT, INT, INT, INT, HANDLE, c_void_p)
user32.TrackPopupMenuEx.argtypes = (HANDLE, UINT, INT, INT, HANDLE, c_void_p)

user32.RegisterShellHookWindow.argtypes = (HWND,)

########################################
# UxTheme
########################################
uxtheme.SetWindowTheme.argtypes = (HANDLE, LPCWSTR, LPCWSTR)

uxtheme.ShouldAppsUseDarkMode = uxtheme[136]

uxtheme.ShouldSystemUseDarkMode = uxtheme[138]

# using fnAllowDarkModeForWindow = bool (WINAPI*)(HWND hWnd, bool allow); // ordinal 133
uxtheme.AllowDarkModeForWindow = uxtheme[133]
uxtheme.AllowDarkModeForWindow.argtypes = (HWND, BOOL)

# SetPreferredAppMode = PreferredAppMode(WINAPI*)(PreferredAppMode appMode);
uxtheme.SetPreferredAppMode = uxtheme[135]  # ordinal 135, in 1903

uxtheme.FlushMenuThemes = uxtheme[136]

uxtheme.OpenThemeData.argtypes = (HWND, LPCWSTR)
uxtheme.OpenThemeData.restype = HANDLE

# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-getthemepartsize
uxtheme.GetThemePartSize.argtypes = (HANDLE, HDC, INT, INT, POINTER(RECT), UINT, POINTER(SIZE))  # HTHEME, THEMESIZE

# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-drawthemebackground
uxtheme.DrawThemeBackground.argtypes = (HANDLE, HDC, INT, INT, POINTER(RECT), POINTER(RECT))  # HTHEME, HDC
