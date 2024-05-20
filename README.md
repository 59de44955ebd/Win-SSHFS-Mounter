# Win-SSHFS-Mounter

Win-SSHFS-Mounter is a small System Tray application for Windows that allows to mount and unmount [SSHFS](https://github.com/libfuse/sshfs) Drives. It depends on [WinFsp](https://winfsp.dev/). Other than that it has no more dependancies, it does **not** use [sshfs-win](https://github.com/winfsp/sshfs-win), but instead bundled unaltered versions of [Cygwin](https://www.cygwin.com/)'s sshfs, ssh, sshpass and puttygen.

## Setup and usage

* Install [WinFsp](https://winfsp.dev/).
* Install and run [Win-SSHFS-Mounter](https://github.com/59de44955ebd/Win-SSHFS-Mounter/releases), or use the portable version without setup.
* Configured SSHFS-connections/drives can be mounted/unmounted directly from the systray icon's popup menu.
* The GUI for adding/editing connections can be opened by double clicking on the systray icon or selecting "Edit Connections..." in the popup menu.
* Connections are stored in the registry (in userspace) and erased when you uninstall the app. In case of the portable version you can execute enclosed "remove-settings.reg" to remove the registry key.
* If you choose "Password (saved)" as authentication method, the password stored in the registry is encrypted using a simple XOR encryption, which only prevents to obtain it directly without having the application's source code. Other authentication methods like "Private Key File" are usually a better choice.

## Features

* Import sites from [FileZilla](https://filezilla-project.org/) (sitemanager.xml/sites.xml) and [WinSCP](https://winscp.net/) (WinSCP.ini), including saved passwords.
* When importing sites from FileZilla or WinSCP, [PuTTY](https://www.putty.org/) private key files (.ppk) can optionally be converted to OpenSSH format on the fly.

## Screenshots

*Win-SSHFS-Mounter in System Tray (Windows 11)*  
![Win-SSHFS-Mounter in System Tray](screenshots/systray.png)

*Win-SSHFS-Mounter GUI (Windows 11)*  
![Win-SSHFS-Mounter GUI](screenshots/gui.png)
