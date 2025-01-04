---
title: Arch Linux 安装流程
date: 2023-02-09T18:23:54+08:00
categories: ["linux"]
tags: ["Arch Linux", "linux"]
draft: false
---

Arch Linux 的安装流程，主要参考 Arch Linux 官方文档 [Installation guide - ArchWiki](https://wiki.archlinux.org/title/Installation_guide)。

## 1 安装前准备

### 1.1 下载安装镜像

在 [Arch Linux 清华源](https://mirrors.tuna.tsinghua.edu.cn/archlinux/iso/)，下载安装镜像 `archlinux-version-x86_64.iso`。

下载完成后，可以使用 `sha256sum` 检查镜像文件的完整性。

### 1.2 刻录镜像

在 Windows 系统下，可以使用 Rufus、BalenaEtcher、Ventoy 等软件，将安装镜像刻录到 U 盘中。

在 Linux 和 MacOS 系统下，可以使用 `dd` 命令刻录镜像：

```sh
sudo dd if=/path/to/file.iso of=/dev/sdX bs=4M oflag=sync status=progress
```

## 2 正式安装

重启电脑，进入 BIOS 界面，设置首选启动项为 U 盘。从 U 盘启动，进入安装环境。

> **提示**：在连接网络并更新系统时钟后，后续的安装步骤也可以使用自动化安装脚本 `archinstall` 来完成，对照手动安装的步骤进行配置。

### 2.1 验证启动模式

```sh
cat /sys/firmware/efi/fw_platform_size
```

如果该命令返回 `64`，则系统以 UEFI 模式启动，可以继续进行以下步骤。

### 2.2 连接网络

验证网络连接：

```sh
ping archlinux.org
```

如果是有线网络，应该会自动连接。

如果是无线网络，执行 `iwctl` 进入 `iwd` 提示符（执行 `exit` 退出），连接网络：

```
# 将以下命令中的 <device> 替换为你的网卡设备
# 将以下命令中的 <SSID> 替换为无线网络的 SSID
device list                     # 列出网卡设备
station <device> scan           # 扫描无线网络（无输出）
station <device> get-networks   # 显示扫描结果
station <device> connect <SSID> # 连接无线网络
```

### 2.3 更新系统时钟

在安装环境中，建立网络连接后，系统时间将自动同步。
执行以下命令，检查系统时间是否已经同步：

```sh
timedatectl
```

如果系统时间未同步，可以执行以下命令，设置自动同步：

```sh
timedatectl set-ntp true
```

### 2.4 硬盘分区

以下分别介绍 Ext4 和 Btrfs 两种文件系统的推荐分区方案，选择其一即可。

执行 `lsblk` 列出所有的硬盘设备。

使用 `fdisk` 或 `cfdisk` 进行硬盘分区。
执行 `fdisk /dev/<disk>` 或 `cfdisk /dev/<disk>` 进入硬盘分区界面。

#### 2.4.1 Ext4 文件系统

参考分区表如下：

| 分区 Partition | 文件系统 File System | 大小 Size | 挂载点 Mount Point |
| -------------- | -------------------- | --------- | ------------------ |
| `/dev/sda1`    | EFI System Partition | 512 MB    | `/mnt/boot`        |
| `/dev/sda2`    | Ext4                 | 80 GB     | `/mnt`             |
| `/dev/sda3`    | Linux Swap           | 16 GB     | [SWAP]             |
| `/dev/sda4`    | Ext4                 | 剩余空间  | `/mnt/home`        |

格式化硬盘分区：

```sh
mkfs.fat -F 32 /dev/<efi_system_partition>
mkfs.ext4 /dev/<root_partition>
mkswap /dev/<swap_partition>
mkfs.ext4 /dev/<home_partition>
```

挂载硬盘分区：

```sh
mount /dev/<root_partition> /mnt
mount --mkdir /dev/<efi_system_partition> /mnt/boot
swapon /dev/<swap_partition>
mount --mkdir /dev/<home_partition> /mnt/home
```

> **注意**：挂载硬盘分区时，必须依照挂载点的层次关系，按顺序挂载。
> 即首先挂载 Root 分区，然后才能挂载 EFI 和 Home 分区。

#### 2.4.2 Btrfs 文件系统

对于 Btrfs 文件系统，可以采用扁平化布局，即除了 EFI 分区和交换分区外，其他分区都可以变成同一个分区下的子卷。

参考分区表如下：

| 分区 Partition | 文件系统 File System | 大小 Size | 挂载点 Mount Point |
| -------------- | -------------------- | --------- | ------------------ |
| `/dev/sda1`    | EFI System Partition | 512 MB    | `/mnt/boot`        |
| `/dev/sda2`    | Linux Swap           | 16 GB     | [SWAP]             |
| `/dev/sda3`    | Btrfs                | 剩余空间  |                    |

对于 `/dev/sda3` 分区，其子卷的布局如下：

| 子卷 Subvolume | 挂载点 Mount Point | 挂载选项 Mount Options           |
| -------------- | ------------------ | -------------------------------- |
| @              | `/mnt`             | `noatime, compress=zstd`         |
| @home          | `/mnt/home`        | `noatime, compress=zstd`         |
| @var-log       | `/mnt/var/log`     | `noatime, compress=zstd`, no CoW |
| @var-cache     | `/mnt/var/cache`   | `noatime, compress=zstd`, no CoW |
| @var-tmp       | `/mnt/var/tmp`     | `noatime, compress=zstd`, no CoW |

在完成硬盘分区后，格式化硬盘分区：

```sh
mkfs.fat -F 32 /dev/<efi_system_partition>
mkswap /dev/<swap_partition>
mkfs.btrfs /dev/<btrfs_partition>
```

然后，挂载硬盘分区。首先，挂载 Btrfs 分区：

```sh
# 创建子卷
mount /dev/<btrfs_partition> /mnt
btrfs subvolume create /mnt/@{,home,var-log,var-cache,var-tmp}
umount /mnt

# 挂载子卷
mount /dev/<btrfs_partition> /mnt -o subvol=@,noatime,compress=zstd
mount --mkdir /dev/<btrfs_partition> /mnt/home -o subvol=@home,noatime,compress=zstd
mount --mkdir /dev/<btrfs_partition> /mnt/var/log -o subvol=@var-log,noatime,compress=zstd
mount --mkdir /dev/<btrfs_partition> /mnt/var/cache -o subvol=@var-cache,noatime,compress=zstd
mount --mkdir /dev/<btrfs_partition> /mnt/var/tmp -o subvol=@var-tmp,noatime,compress=zstd

# 禁用部分子卷的 CoW 特性
chattr +C /mnt/var/{log,cache,tmp}
```

然后，挂载 EFI 和交换分区：

```sh
mount --mkdir /dev/<efi_system_partition> /mnt/boot
swapon /dev/<swap_partition>
```

### 2.5 安装系统基本软件包

首先，更换 pacman 的镜像源。在 `/etc/pacman.d/mirrorlist` 文件的开头添加：

```
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
```

然后，执行以下命令：

```sh
# 如果使用 AMD 处理器，将 intel-ucode 替换为 amd-ucode
# 可以将 neovim 替换为其他文本编辑器
# 如果不使用 Btrfs 文件系统，则删除 btrfs-progs
pacstrap -K /mnt base linux linux-firmware intel-ucode networkmanager neovim btrfs-progs
```

## 3 系统初步配置

### 3.1 生成 Fstab 文件

```sh
genfstab -U /mnt >> /mnt/etc/fstab
```

### 3.2 Chroot

```sh
arch-chroot /mnt
```

### 3.3 设置时区

```sh
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
hwclock --systohc
```

### 3.4 本地化设置

在 `/etc/locale.gen` 文件中，将 `en_US.UTF-8 UTF-8` 和 `zh_CN.UTF-8 UTF-8` 取消注释。

然后，执行以下命令：

```
locale-gen
```

新建 `/etc/locale.conf` 文件，并添加内容：

```
LANG=en_US.UTF-8
```

### 3.5 配置网络

新建 `/etc/hostname` 文件，添加主机名，例如：`myhostname`。

在 `/etc/hosts` 文件中，添加以下内容（将 `myhostname` 替换为自己的主机名）：

```
127.0.0.1 localhost
::1 localhost
127.0.1.1 myhostname.localdomain myhostname
```

### 3.6 修改 mkinitcpio 配置

如果使用 Btrfs 文件系统，需要修改 `/etc/mkinitcpio.conf` 文件，在 `MODULES=()` 中添加 `btrfs`。

然后，执行命令：

```sh
mkinitcpio -P
```

### 3.7 安装 GRUB

安装 `grub` 和 `efibootmgr`。

> **建议**：在进行后续步骤前，执行 `lsblk`，并检查 `EFI System Partition` 的挂载点，确保其已被成功挂载。如果没有成功挂载，请检查挂载硬盘分区的顺序。

执行以下命令：

```sh
# 注意：在 Chroot 后，参考挂载点下的 <esp_mount_point> 为 /boot，而不是 /mnt/boot
grub-install --target=x86_64-efi --efi-directory=<esp_mount_point> --bootloader-id=GRUB
grub-mkconfig -o <esp_mount_point>/grub/grub.cfg
```

### 3.8 设置 root 用户的密码

执行 `passwd`，并输入要为 root 用户设置的密码。

### 3.9 重启

```sh
exit
umount -R /mnt
reboot
```

## 4 重启后简单配置

### 4.1 连接网络

启动网络服务：

```sh
systemctl enable --now NetworkManager.service
```

如果是无线网络，可以执行 `nmcli` 或 `nmtui`，进行连接。

### 4.2 添加普通用户

添加用户名为 `username` 的普通用户：

```sh
useradd -G wheel -m username
passwd username
```

安装 `sudo`，并为新添加的用户设置 root 权限。
执行 `visudo` 命令来编辑 `/etc/sudoers` 文件，解除以下一行的注释：

```
%wheel ALL=(ALL:ALL) ALL
```

执行 `exit` 退出 root 用户的登录，并登录到 `username` 用户。

至此，Arch Linux 已经完成安装。
