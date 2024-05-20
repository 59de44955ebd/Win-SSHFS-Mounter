import os
from winapp.const import WM_USER


APP_NAME = 'Win-SSHFS-Mounter'
APP_CLASS = 'WinSSHFSMounterClass'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_DIR = os.path.join(APP_DIR, 'resources', 'cygwin', 'bin')

MSG_TRAYICON = WM_USER + 1

IDM_SETTINGS = 1
IDM_QUIT = 2

# Icon IDs
IDI_APPICON = 1

IDC_OK = 1
IDC_CANCEL = 2
IDC_EDIT = 3

CON_ID_START = 100

BUTTON_WIDTH = 140
BUTTON_HEIGHT = 23
MARGIN = 10

# Simple XOR encryption of passwords stored in the Windows Registry
# This only prevents reading the passwords from registry directly without having the Python source code
MASTER_KEY = b'uLXdt2@X*eVh5a8194l!4ySFpvkS!2_092Mj21hcJ3W64qJG&rayCg_J3D9$@aO)'

POLL_PERIOD_MS = 2000

MAX_RECONNECTS = 3
SSH_CONNECT_TIMEOUT_SEC = 2

IDD_DIALOG1                     =101
IDC_EDIT_NAME                   =1000
IDC_EDIT_HOST                   =1001
IDC_EDIT_PORT                   =1002
IDC_EDIT_USER                   =1003
IDC_EDIT_PATH                   =1004
IDC_COMBO_LETTER                =1005
IDC_COMBO_AUTH                  =1006

IDC_STATIC_PASSWORD             =1008
IDC_EDIT_PASSWORD               =1009

IDC_STATIC_KEY                  =1010
IDC_EDIT_KEY                    =1011

IDC_SELECT_KEY                  =1014
IDC_CHECK_AUTOCONNECT           =1012
IDC_CHECK_RECONNECT             =1013

IDC_STATIC                      =-1
