---
title: KDE Plasma 5 安装流程
date: 2022-05-02T02:07:54+08:00
categories: ["linux"]
tags: ["KDE", "linux"]
draft: false
---

Arch Linux 安装完成后，为了方便使用，可以选择安装桌面环境或窗口管理器。
常用的桌面环境有 KDE Plasma、GNOME、XFCE 等，可以查阅 [Desktop environment - ArchWiki](https://wiki.archlinux.org/title/Desktop_environment) 和 [Window manager - ArchWiki](https://wiki.archlinux.org/title/Window_manager) 获取更多信息。

下面介绍如何安装 KDE Plasma 5 桌面环境。

## 1 安装显示服务器

```shell
sudo pacman -S xorg
```

## 2 安装 KDE 软件包

```shell
sudo pacman -S plasma
sudo pacman -S kde-applications # 可选
```

## 3 显示管理器

选择是否安装显示管理器，进行相应步骤。

### 3.1 安装显示管理器

```shell
sudo pacman -S sddm
systemctl enable sddm.service
```

安装显示管理器后，在开机时会有图形登录界面，比较方便。

### 3.2 不安装显示管理器

如果不安装显示管理器，需要进行以下配置：

```shell
cp /etc/X11/xinit/xinitrc ~/.xinitrc
```

然后，在 `~/.xinitrc` 中添加以下内容：

```
export DESKTOP_SESSION=plasma
exec startplasma-x11
```

配置完成后，可以在开机后，手动执行 `startx` 进入桌面环境。

如果需要在登录后，自动执行 `startx`，可以将以下内容添加到 Shell 的配置文件：

```shell
if [ -z "${DISPLAY}" ] && [ "${XDG_VTNR}" -eq 1 ]; then
    exec startx
fi
```

重启后，进入桌面环境。
