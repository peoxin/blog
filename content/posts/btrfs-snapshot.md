---
title: 在 Btrfs 文件系统中配置自动快照
date: 2025-01-05T00:45:06+08:00
categories: ["linux"]
tags: ["btrfs", "linux"]
draft: false
---

在根据 Arch Linux 安装流程完成系统安装后，如果选择了 Btrfs 文件系统，那么可以进行自动快照的配置。

在本文中，选择 `snapper` 作为快照管理的工具。以下介绍其配置和使用方法。

## 1 使用 snapper 为根目录配置自动快照

### 1.1 安装 snapper

```sh
sudo pacman -S snapper
```

### 1.2 创建快照配置

执行以下命令，为挂载在 `/` 目录下的 Btrfs 子卷创建名为 `root` 的快照配置：

```sh
sudo snapper -c root create-config /
```

执行该命令后，会在 `/etc/snapper/configs` 目录下生成名为 `root` 的配置文件，并在 `/.snapshots` 处创建一个名为 `/.snapshots` 的子卷。

通过以下方法，可以将所使用的快照子卷修改之前创建的 `@snapshots` 子卷：

```sh
# 删除 /.snapshots 子卷，同时删除 /.snapshots 目录
sudo btrfs subvolume delete /.snapshots

# 创建 @snapshots 子卷，并确保其为顶级子卷 (subvolid=5) 的子卷
# 不使用 -o subvol 选项，或者使用 -o subvol=/ 选项，可以挂载顶级子卷
sudo mount /dev/<btrfs_partition> /mnt
sudo btrfs subvolume create /mnt/@snapshots
sudo umount /mnt

# 重新创建 /.snapshots 目录
sudo mkdir /.snapshots

# 在 /etc/fstab 中添加条目，参考其他子卷的格式，将 @snapshots 子卷挂载到 /.snapshots 目录
# 添加条目后，重新挂载所有条目
sudo mount -a
```

默认情况下，`snapper` 会每小时自动创建一个快照，并保留一定数量的每小时、每日、每月等快照。相关配置位于快照配置文件的 `TIMELINE_*` 部分，可以根据需要修改。

### 1.3 启用自动快照

如果系统中没有安装 `cron` 服务，可以启用 `systemd` 定时器：

```sh
sudo systemctl enable --now snapper-timeline.timer
sudo systemctl enable --now snapper-cleanup.timer
```

如果系统中安装并运行了 `cron` 服务，则将会自动进行定时快照的创建。在这种情况下，需要关闭 `systemd` 定时器，否则可能会导致重复创建快照。

### 1.4 从快照中恢复

首先，找到所要恢复到的快照的编号：

```sh
grep -r "<date>" /.snapshots/*/info.xml
grep -r "<description>" /.snapshots/*/info.xml
```

#### 1.4.1 系统正常启动的情况

如果系统可以正常启动，执行以下命令，从快照中恢复：

```sh
# 从快照 0 恢复到快照 N，0 表示当前状态，N 为要恢复到的快照编号
sudo snapper -c root undochange N..0
```

#### 1.4.2 系统无法启动的情况

如果系统无法启动，可以使用 Arch Linux 安装环境，挂载根目录。然后，执行以下命令，从快照中恢复：

```sh
# N 为要恢复到的快照编号
mount /dev/<btrfs_partition> /mnt
mv /mnt/@ /mnt/@.broken
btrfs subvolume snapshot /mnt/@snapshots/.snapshots/N/snapshot /mnt/@
btrfs subvolume delete /mnt/@.broken
umount /mnt
```

> 如果不执行 `mv /mnt/@ /mnt/@.broken` 命令，那么因为 `@` 子卷已经存在，在 `btrfs subvolume snapshot` 时，就会创建挂载于 `/snapshot` 目录的 `/snapshot` 子卷，而不是覆盖 `@` 子卷。

### 1.5 使用 snap-pac

```sh
sudo pacman -S snap-pac
```

`snap-pac` 可以在 `pacman` 安装、删除和更新软件包的前后，自动地创建一对快照。默认情况下，它使用名为 `root` 的配置文件，来创建手动快照，因此无需额外配置。

## 2 更多使用方法

### 2.1 手动创建快照

除了自动创建快照外，也可以手动创建快照。使用以下命令，根据名为 `config` 的配置，创建一个快照：

```sh
sudo snapper -c config create --description desc
```

也可以在执行重要命令的前后，手动创建一对快照：

```sh
sudo snapper -c config create --command cmd
```

默认情况下，手动创建的快照不会被自动清理。

### 2.2 查看快照

列出所有的快照配置：

```sh
snapper list-configs
```

列出名为 `config` 的配置下的所有快照：

```sh
sudo snapper -c config list
```

### 2.3 删除快照

删除名为 `config` 的配置下的编号为 `N` 的快照：

```sh
sudo snapper -c config delete N
```
