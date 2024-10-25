---
title: Arch Linux 安装流程
date: 2023-02-09T18:23:54+08:00
categories: ["Linux"]
tags: ["Arch Linux", "Linux"]
draft: false
---

Arch Linux 的安装流程，主要参考 Arch Linux 官方文档 [Installation guide - ArchWiki](https://wiki.archlinux.org/title/Installation_guide)。

## 1 安装前准备

### 1.1 下载安装镜像

在 [Arch Linux 清华源](https://mirrors.tuna.tsinghua.edu.cn/archlinux/iso/)，下载安装镜像 `archlinux-version-x86_64.iso`。

### 1.2 验证签名（可选）

在下载安装镜像的相同网址，下载 PGP 签名文件 `archlinux-version-x86_64.iso.sig`，并复制到 ISO 镜像所在的路径下。使用 `GnuPG` 工具，验证安装镜像的完整性：

```shell
gpg --keyserver-options auto-key-retrieve --verify archlinux-version-x86_64.iso.sig
```

### 1.3 刻录镜像

Windows 系统下使用 `rufus` 软件，将安装镜像刻录到 U 盘中。

Linux 系统下使用 `dd` 命令，刻录镜像。

## 2 正式安装

重启电脑，进入 BIOS 界面，设置首选启动项为 U 盘。从 U 盘启动，进入安装环境。

### 2.1 验证启动模式

```shell
ls /sys/firmware/efi/efivars
```

如果能够正确显示路径信息，无错误提示，说明启动模式为 UEFI。

### 2.2 连接网络

验证网络连接：

```shell
ping baidu.com
```

如果是有线网络，应该会自动连接。

如果是无线网络，执行 `iwctl` 进入 `iwd` 提示符（执行 `exit` 退出提示符），连接网络：

```
# 将下列命令中的 <device> 替换为你的网卡设备
# 将下列命令中的 <SSID> 替换为无线网络的 SSID
device list                     # 列出网卡设备
station <device> scan           # 扫描无线网络
station <device> get-networks   # 显示扫描结果
station <device> connect <SSID> # 连接无线网络
```

### 2.3 更新系统时钟

```shell
timedatectl set-ntp true
```

更新系统时钟后，可以执行 `timedatectl status` 检查。

### 2.4 硬盘分区

执行 `fdisk -l` 列出硬盘设备。

推荐使用 `cfdisk` 进行硬盘分区。执行 `cfdisk /dev/<disk-name>` 进入硬盘分区界面。

参考分区表如下：

| 分区 Partition | 文件系统 File System | 大小 Size | 挂载点 Mount Point |
| -------------- | -------------------- | --------- | ------------------ |
| /dev/sda1      | EFI System Partition | 300 MB    | /mnt/boot          |
| /dev/sda2      | ext4                 | 20 GB     | /mnt               |
| /dev/sda3      | Linux Swap           | 8 GB      | [SWAP]             |
| /dev/sda4      | ext4                 | 剩余空间  | /mnt/home          |

完成分区后，可以执行 `lsblk` 命令检查分区情况。

### 2.5 格式化硬盘分区

```shell
mkfs.fat -F 32 /dev/<efi_system_partition>
mkfs.ext4 /dev/<root_partition>
mkswap /dev/<swap_partition>
mkfs.ext4 /dev/<home_partition>
```

### 2.6 挂载硬盘分区

```shell
mount /dev/<root_partition> /mnt
mount --mkdir /dev/<efi_system_partition> /mnt/boot
swapon /dev/<swap_partition>
mount --mkdir /dev/<home_partition> /mnt/home
```

> **注意**：挂载硬盘分区时，必须首先挂载 `Root` 分区，然后才能挂载 `ESP` 分区。否则，`/mnt/boot` 会发生冲突，导致出错。

### 2.7 更换镜像源

在 `/etc/pacman.d/mirrorlist` 文件的最顶端添加：

```
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
```

### 2.8 安装系统必需软件包

```shell
pacstrap /mnt base linux linux-firmware
```

## 3 系统初步配置

### 3.1 生成 Fstab 文件

```shell
genfstab -U /mnt >> /mnt/etc/fstab
```

### 3.2 Chroot

```shell
arch-chroot /mnt
```

### 3.3 设置时区

```shell
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
timedatectl set-ntp true
hwclock --systohc
```

### 3.4 本地化设置

首先安装 `vim`。

在 `/etc/locale.gen` 文件中，将 `en_US.UTF-8 UTF-8` 和 `zh_CN.UTF-8 UTF-8` 取消注释。然后，执行 `locale-gen` 命令。

新建 `/etc/locale.conf` 文件，并添加内容 `LANG=en_US.UTF-8`。

### 3.5 配置网络

新建 `/etc/hostname` 文件，添加主机名，例如：`myhostname`。

在 `/etc/hosts` 文件中，添加以下内容（将 `myhostname` 替换为自己的主机名）：

```
127.0.0.1 localhost
::1 localhost
127.0.1.1 myhostname.localdomain myhostname
```

### 3.6 设置 root 用户的密码

执行 `passwd`，并输入要为 root 用户设置的密码。

### 3.7 安装 GRUB

安装 `grub` 和 `efibootmgr`。

> **建议**：在进行后续步骤前，执行 `lsblk`，并检查 `EFI System Partition` 的挂载点，确保其已被成功挂载。如果没有成功挂载，请检查挂载硬盘分区的顺序。

执行以下命令。
需要注意的是，在 Chroot 后，参考挂载点下的 `<esp_mount_point>` 为 `/boot`，而不是 `/mnt/boot`。

```shell
grub-install --target=x86_64-efi --efi-directory=<esp_mount_point> --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

### 3.8 安装文本编辑器和网络服务

```shell
pacman -S vim dhcpcd networkmanager
```

> 如果不安装网络服务，新系统将无法联网。
> 如果进入新系统后，发现忘记安装网络服务，可以再次从 U 盘启动，进入安装环境。运行命令：
>
> ```
> mount /dev/<root_partition> /mnt
> arch-chroot /mnt
> ```
>
> 然后安装网络服务，并继续进行以下**重启**步骤，进入新系统。

### 3.9 重启

```shell
exit
umount -R /mnt
reboot
```

## 4 重启后简单配置

### 4.1 连接网络

#### 4.1.1 有线网络

运行以下命令即可，无需额外操作：

```shell
systemctl start dhcpcd.service
systemctl enable dhcpcd.service
```

#### 4.1.2 无线网络

首先，启动网络服务：

```shell
systemctl start dhcpcd.service
systemctl enable dhcpcd.service
systemctl start NetworkManager.service
systemctl enable NetworkManager.service
```

然后，执行 `nmtui`，连接无线网络。

### 4.2 添加普通用户

添加用户名为 `username` 的普通用户：

```shell
useradd -m username
passwd username
```

安装 `sudo`，并为新添加的用户设置 root 权限。
在 `/etc/sudoers` 文件中的 `root ALL=(ALL:ALL) ALL` 一行下，添加 `%wheel ALL=(ALL:ALL) ALL`。
然后，将用户添加到 `wheel` 用户组中：

```
usermod -aG wheel username
```

执行 `exit` 退出 root 用户的登录，并登录到 `username` 用户。

至此，Arch Linux 已经完成安装。
