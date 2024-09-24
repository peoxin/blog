---
title: Arch Linux + KDE 的安装和配置
date: 2022-05-02T02:07:54+08:00
draft: true
---

{% note warning %}
此教程版本较旧，尚未更新。建议对照 Arch Linux 官方文档进行阅读！
{% endnote %}

如果遇到任何问题，请优先查阅Arch Linux官方文档[ArchWiki](https://wiki.archlinux.org/)。

## 安装Arch Linux

Arch Linux的安装流程，主要参考Arch Linux官方文档[Installation guide - ArchWiki](https://wiki.archlinux.org/title/Installation_guide)。

### 安装前准备

#### 下载安装镜像

在[Arch Linux 清华源](https://mirrors.tuna.tsinghua.edu.cn/archlinux/iso/)，下载ISO安装镜像`archlinux-version-x86_64.iso`。

#### 验证签名

在下载安装镜像的相同网址，下载PGP签名文件`archlinux-version-x86_64.iso.sig`，并复制到ISO镜像所在的文件夹。使用`GnuPG`工具，验证安装镜像的完整性：

```shell
gpg --keyserver-options auto-key-retrieve --verify archlinux-version-x86_64.iso.sig
```

#### 刻录镜像

Windows系统下使用`rufus`软件，将安装镜像刻录到U盘中。

Linux系统下使用`dd`命令，刻录镜像。

### 正式安装

#### 进入安装环境

重启电脑，进入BIOS界面设置首选启动项为U盘。从U盘启动，进入安装环境。

#### 验证启动模式

```shell
ls /sys/firmware/efi/efivars
```

如果能够正确显示路径信息，无错误提示，说明启动模式为UEFI。

#### 连接网络

验证网络连接：

```shell
ping baidu.com
```

如果是有线网络，应该会自动连接。

如果是无线网络，执行`iwctl`进入`iwd`提示符（执行`exit`退出提示符），并执行：

```
device list # 列出网卡设备，将下列命令的<device>更换为你的网卡设备
station <device> scan # 扫描可用无线网络（该命令无输出）
station <device> get-networks # 显示扫描的结果
station <device> connect <SSID> # 连接无线网络，将<SSID>更换为无线网络的SSID
```

#### 更新系统时钟

```shell
timedatectl set-ntp true
```

更新系统时钟后，可以执行`timedatectl status`检查。

#### 硬盘分区

推荐使用`cfdisk`进行硬盘分区。执行`cfdisk /dev/<disk-name>`进入硬盘分区界面。参考分区表如下：

| 分区 Partition | 文件系统 File System | 大小 Size | 挂载点 Mount Point |
| -------------- | -------------------- | --------- | ------------------ |
| /dev/sda1      | EFI System Partition | 300 MB    | /mnt/boot          |
| /dev/sda2      | ext4                 | 20 GB     | /mnt               |
| /dev/sda3      | Linux Swap           | 8 GB      | [SWAP]             |
| /dev/sda4      | ext4                 | 剩余空间  | /mnt/home          |

分区完成后，可以执行`cfdisk`，`fdisk -l`，`lsblk -f`等命令检查分区情况。

#### 格式化硬盘分区

```shell
mkfs.fat -F 32 /dev/<efi_system_partition> # 参考分区下<efi_system_partition>为sda1
mkfs.ext4 /dev/<root_partition> # 参考分区下<root_partition>为sda2
mkswap /dev/<swap_partition> # 参考分区下<swap_partition>为sda3
mkfs.ext4 /dev/<home_partition> # 参考分区下<home_partition>为sda4
```

#### 挂载硬盘分区

```shell
mount /dev/<root_partition> /mnt # 参考分区下<root_partition>为sda2
mount --mkdir /dev/<efi_system_partition> /mnt/boot # 参考分区下<efi_system_partition>为sda1
swapon /dev/<swap_partition> # 参考分区下<swap_partition>为sda3
mount --mkdir /dev/<home_partition> /mnt/home # 参考分区下<home_partition>为sda4
```

> 挂载硬盘分区时，必须首先挂载`Root`分区，然后才能挂载`ESP`分区。否则，`/mnt/boot`会发生冲突，导致出错。

#### 更换镜像源

```shell
vim /etc/pacman.d/mirrorlist
```

在文件最顶端添加：

```
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
```

#### 安装系统必需软件包

```shell
pacstrap /mnt base linux linux-firmware
```

### 系统初步配置

#### 生成Fstab文件

```shell
genfstab -U /mnt >> /mnt/etc/fstab
```

执行`cat /mnt/etc/fstab`，检查是否正确。如果不正确，可以尝试手动修改，参考[Fstab - ArchWiki](https://wiki.archlinux.org/title/Fstab)。修改完成后，可以执行`systemctl daemon-reload`，进行刷新。

#### Chroot

```shell
arch-chroot /mnt
```

#### 设置时区

```shell
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
hwclock --systohc
```

#### 本地化设置

安装`vim`，然后执行：

```shell
vim /etc/locale.gen
```

将`en_US.UTF-8 UTF-8`和`zh_CN.UTF-8 UTF-8`取消注释。然后执行`locale-gen`命令。

```shell
vim /etc/locale.conf # 新建locale.conf文件
```

添加`LANG=en_US.UTF-8`。

#### 配置网络

```shell
vim /etc/hostname # 新建hostname文件
```

添加主机名，例如：`myhostname`。

```shell
vim /etc/hosts
```

添加以下内容：

```
127.0.0.1 localhost
::1 localhost
127.0.1.1 myhostname.localdomain myhostname # 将myhostname更换为自己的主机名
```

#### 设置root用户的密码

执行`passwd`，并输入要为root用户设置的密码。

#### 安装和配置GRUB

安装`grub`和`efibootmgr`，执行：

```shell
pacman -S grub efibootmgr
```

执行`lsblk -f`，检查`EFI System Partition`的挂载点，确保其已被成功挂载。如果没有成功挂载，检查`Fstab`文件和挂载硬盘分区的顺序。

在以下命令中，用该挂载点代替`<esp_mount_point>`：

```shell
# 参考挂载点下，<esp_mount_point>为/boot，注意并非/mnt/boot
grub-install --target=x86_64-efi --efi-directory=<esp_mount_point> --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

> 注意检查`grub-mkconfig -o /boot/grub/grub.cfg`命令的输出，应该包含以下信息：
>
> `Found linux image: /boot/vmlinuz-linux` > `Found initrd image: /boot/initramfs-linux.img` > `Found fallback initrd image(s) in /boot: initramfs-linux-fallback.img`
>
> 如果无上述信息，说明安装出错。可以检查`Fstab`文件和挂载硬盘分区的顺序。

#### 安装网络工具和文本编辑器

```shell
pacman -S iwd dhcpcd # 网络工具
# 或者安装networkmanager，使用nmcli或nmtui配置，该工具为KDE plasma所需组件
pacman -S vim # 文本编辑器
```

> 如果不安装网络工具，新系统将无法联网。如果进入新系统后，发现忘记安装网络工具，解决方法如下：
>
> 重启并再次从U盘启动，进入安装环境。执行：
>
> `mount /dev/<root_partition> /mnt # 参考分区下<root_partition>为sda2` > `arch-chroot /mnt` > `pacman -S iwd dhcpcd`
>
> 继续进行以下**重启**步骤，进入新系统。

#### 重启

```shell
exit # 退出Chroot
umount -R /mnt # 解除硬盘挂载
reboot # 重启并进入新系统
```

### 重启后简单配置

#### 连接网络

##### 有线网络

```shell
systemctl start dhcpcd.service # 启动dhcpcd服务
systemctl enable dhcpcd.service # 开机自启动dhcpcd服务
```

##### 无线网络

```shell
systemctl start iwd.service # 启动iwd服务
systemctl enable iwd.service # 开机自启动iwd服务
systemctl start dhcpcd.service # 启动dhcpcd服务
systemctl enable dhcpcd.service # 开机自启动dhcpcd服务
```

执行`iwctl`，连接无线网络。

#### 添加普通用户

```shell
useradd -m username # 添加用户名为username的用户
passwd username # 为用户username设置密码
# 添加用户的更多选项
# useradd -m -G additional_groups -s login_shell username
```

为新添加的普通用户设置root权限：

```shell
pacman -S sudo
vim /etc/sudoers
```

打开`/etc/sudoers`文件后，在`root ALL=(ALL:ALL) ALL`一行下，添加`username ALL=(ALL:ALL) ALL`。

执行`exit`退出root用户的登录，并登录`username`用户。

至此，Arch Linux已经完成安装。

## 安装KDE桌面环境

Arch Linux安装完成后，为了方便使用，可以选择安装桌面环境或窗口管理器。常用的桌面环境有KDE Plasma、GNOME、XFCE等，可以查阅[Desktop environment - ArchWiki](https://wiki.archlinux.org/title/Desktop_environment)和[Window manager - ArchWiki](https://wiki.archlinux.org/title/Window_manager)获取更多信息。

下面安装KDE Plasma桌面环境。

### 安装显示服务器

```shell
sudo pacman -S xorg
```

### 安装KDE软件包

```shell
sudo pacman -S plasma kde-applications
```

### 显示管理器

选择是否安装显示管理器，进行对应步骤。

#### 安装显示管理器

```shell
sudo pacman -S sddm
systemctl enable sddm.service # 开机自启动sddm服务
```

安装显示管理器后，在开机时会有图形登录界面，比较方便。

#### 不安装显示管理器

如果不安装显示管理器，需要进行以下配置：

```shell
cp /etc/X11/xinit/xinitrc ~/.xinitrc
```

执行`vim ~/.xinitrc`，添加以下内容：

```
export DESKTOP_SESSION=plasma
exec startplasma-x11
```

配置完成后，可以在开机后，手动执行`startx`进入桌面环境。

如果需要在登录后，自动执行`startx`，可以选择进行以下配置：

打开你所使用的Shell的启动配置文件，例如：如果使用`bash`，则执行`vim ~/.bash_profile`；如果使用`zsh`，则执行`vim ~/.zprofile`。也可以打开Shell的全局启动配置文件，执行`vim /etc/profile`。

在Shell的启动配置文件中添加以下内容：

```shell
if [ -z "${DISPLAY}" ] && [ "${XDG_VTNR}" -eq 1 ]; then
    exec startx
fi
```

> 执行`echo $SHELL`可以查看当前使用的Shell
>
> 执行`chsh -l`可以列出可用的Shell
>
> 执行`chsh -s <full_path_to_shell>`可以改变使用的Shell
>
> 查阅[Bash - ArchWiki](https://wiki.archlinux.org/title/Bash)、[Zsh - ArchWiki](https://wiki.archlinux.org/title/Zsh)和[Command-line shell - ArchWiki](https://wiki.archlinux.org/title/Command-line_shell)了解更多内容

### 进入桌面环境

重启后，进入桌面环境。

## 更多配置

### 安装Git

```shell
sudo pacman -S git
```

### 添加Arch Linux CN源

执行`vim /etc/pacman.conf`，添加以下内容：

```
[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
```

然后执行：

```shell
sudo pacman -S archlinuxcn-keyring # 导入GPG key
```

### AUR

安装AUR软件仓库中的软件包，有以下两种方法。

#### 手动安装AUR软件包

访问[AUR](https://aur.archlinux.org/)，获取所要安装的软件包的Git Clone URL。进入合适的目录，执行命令：

```shell
git clone <git_clone_url> # 将<git_clone_url>更换为所要安装软件包的Git Clone URL
cd <package_name> # 将<package_name>更换为所要安装软件包的名字，进入软件安装包目录
makepkg -si # 安装软件包
```

#### 使用AUR助手

可以按照手动安装AUR软件包的方法，安装`yay`或其他AUR助手。参考：[GitHub - Jguer/yay](https://github.com/Jguer/yay)。

使用`yay`安装软件包：

```shell
yay -S <package_name> # 将<package_name>更换为所要安装软件包的名字
```

### 安装中文输入法

此处选择安装`fcitx5`输入法框架：

```shell
sudo pacman -S fcitx5-im # fcitx5-im包含fcitx5、fcitx5-configtool、fcitx5-gtk、fcitx5-qt
```

安装中文输入法：

```shell
# 选择其中一个安装，或者全部安装
# 推荐仅安装fcitx5-chinese-addons
sudo pacman -S fcitx5-chinese-addons
sudo pacman -S fcitx5-rime
```

配置环境变量，执行`vim /etc/environment`，添加以下内容：

```
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
```

如果正在使用GNOME、KDE Plasma、XFCE等兼容XDG的桌面环境，在开机后`fcitx5`应该可以自启动。

> 配置环境变量的更多方法，参考[Environment variables - ArchWiki](https://wiki.archlinux.org/title/Environment_variables)

### 安装字体

```shell
sudo pacman -S <font_name> # 将<font_name>更换为字体名
```

### 配置Shell

此处选择安装并配置`zsh`为默认Shell。执行命令：

```shell
sudo pacman -S zsh
chsh -s /bin/zsh # 或者chsh -s /usr/bin/zsh
```

使用`Oh My Zsh`辅助配置`zsh`。安装`Oh My Zsh`：

```shell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

> `Oh My Zsh`的配置，参考[ohmyzsh/ohmyzsh Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki)
>
> 推荐主题：`robbyrussell`、`agnoster`

### 配置Vim

此处安装并使用`neovim`。执行命令：

```shell
sudo pacman -S neovim
```

`neovim`的配置文件路径：`~/.config/nvim/init.vim`

> `neovim`的配置，参考[neovim/neovim](https://github.com/neovim/neovim)

### 安装其他软件包

| 软件       | AUR软件包                                                |
| ---------- | -------------------------------------------------------- |
| Clash      | `clash-for-windows-bin`                                  |
| Edge       | `microsoft-edge-stable-bin`                              |
| 网易云音乐 | `netease-cloud-music`                                    |
| 微信       | `deepin-wine-wechat`                                     |
| QQ         | `deepin-wine-qq`                                         |
| WPS        | `wps-office-cn`、`wps-office-mui-zh-cn`、`ttf-wps-fonts` |
| Typora     | `typora`或`typora-free`                                  |
| Latte Dock | `latte-dock`                                             |
| MarkText   | `marktext-bin`                                           |

#### 安装Clash的注意事项

Clash安装完成后，需要配置全局代理，即设置环境变量如下：

```
http_proxy=http://127.0.0.1:7890 # 端口号与Clash设置保持一致
https_proxy=http://127.0.0.1:7890
ftp_proxy=http://127.0.0.1:7890
```

设置环境变量的一种方法：执行`vim /etc/environment`，添加上述内容。

执行`cfw`打开`Clash`。

#### 安装微信的注意事项

`deepin-wine-wechat`依赖`Multilib`仓库中的一些32位库，但Archlinux默认没有开启`Multilib`仓库。

执行`vim /etc/pacman.conf`，取消下列行的注释：

```
[multilib]
Include = /etc/pacman.d/mirrorlist
```

之后更新本地数据库：

```shell
sudo pacman -Sy
```

完成上述操作后，可以正常安装`deepin-wine-wechat`。

> 参考：[vufa/deepin-wine-wechat 常见问题及解决](https://github.com/vufa/deepin-wine-wechat-arch#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98%E5%8F%8A%E8%A7%A3%E5%86%B3)

## 参考

[Archlinux最新安装教程：2020-07 - 知乎](https://zhuanlan.zhihu.com/p/157260502)

[Manjaro KDE 调教配置及美化（2022.01.23）- 知乎](https://zhuanlan.zhihu.com/p/460826583)
