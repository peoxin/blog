---
title: Arch Linux 安装后的配置
date: 2024-11-23T18:59:23+08:00
categories: ["linux"]
tags: ["Arch Linux", linux"]
draft: false
---

在 Arch Linux 安装完成后，可以根据需要进行以下配置。

## 1 安装字体

以下是一些推荐的字体，以及其对应的软件包。

中文字体：

- 思源字体：`noto-fonts-cjk`

外文字体：

- Noto：`noto-fonts`

符号字体：

- Nerd：`ttf-nerd-fonts-symbols`
- Font Awesome：`ttf-font-awesome`

编程字体：

- JetBrains Mono：`ttf-jetbrains-mono`
- Source Code Pro：`adobe-source-code-pro-fonts`
- Hack：`ttf-hack`
- DejaVu：`ttf-dejavu`
- Meslo：`ttf-meslo-nerd`

## 2 解决网络访问问题

### 2.1 更换官方软件仓库的镜像源

为了提高软件包的下载速度，可以更换官方软件仓库的镜像源。
在 `/etc/pacman.d/mirrorlist` 文件的开头添加以下内容：

```
Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch
```

### 2.2 GitHub 访问速度慢

#### 2.2.1 修改 `/etc/hosts` 文件

在不使用网络代理的情况下，可以通过修改 `/etc/hosts` 文件的方法，解决 GitHub 访问速度慢的问题。

通过 [GitHub520](https://github.com/521xueweihan/GitHub520) 项目，可以获得最新的 GitHub IP 地址，然后将其添加到 `/etc/hosts` 文件的末尾即可。
根据该项目的说明，通过 <https://raw.hellogithub.com/hosts> 网址，可以在无需访问 GitHub 的情况下，获得与项目中相同的 GitHub IP 地址。

使用以下命令，可以直接将最新的 GitHub IP 地址，写入到 `/etc/hosts` 文件中：

```
sudo sh -c 'sed -i "/# GitHub520 Host Start/Q" /etc/hosts && curl https://raw.hellogithub.com/hosts >> /etc/hosts'
```

#### 2.2.2 使用 GitHub 镜像

如果修改 `/etc/hosts` 文件后，仍然无法解决 GitHub 访问速度慢的问题，可以考虑使用 GitHub 的镜像。GitHub 的镜像网站数量较多，可以自行搜索，并根据镜像网站的说明操作。

#### 2.2.3 使用网络代理

通过以上两种方法，可以在无法使用网络代理的情况下，解决 GitHub 访问速度慢的问题。
而如果可以正常地使用网络代理，则该问题将不复存在。

### 2.3 配置网络代理

首先，需要下载和安装网络代理软件。要完成这一步操作，可以考虑多种方法：

- 如果该软件在 Arch Linux 的官方软件仓库中，可以直接使用 `pacman` 命令进行安装；
- 如果该软件在 AUR (Arch User Repository) 中，因为 AUR 在中国大陆无法直接访问，所以考虑通过多种方法获得软件包的构建文件，然后手动构建和安装。

安装完成后，还需要进行配置，才能正常地使用网络代理。以下分别通过安装 `clash` 和 `clash-verge-rev-bin` 的例子，进行更详细的说明。

#### 2.3.1 安装和配置 `clash`

`clash` 被包含在 Arch Linux 的官方软件仓库中，可以使用以下命令进行安装：

```
sudo pacman -S clash
```

因为已经更换过官方软件仓库的镜像源，所以这一步操作应该可以顺利完成。

`clash` 的配置文件位于 `~/.config/clash` 目录下，默认配置文件为 `~/.config/clash/config.yaml`。
在启动时，也可以通过 `-f` 参数来指定所使用的配置文件，即：

```
clash -f /path/to/config.yaml
```

所需的配置文件，可以从订阅链接转换获得，并放置到 `~/.config/clash` 目录下。相关的转换工具：[subconverter](https://github.com/tindy2013/subconverter)、[subweb](https://github.com/stilleshan/subweb)。
也可以使用其他客户端转换过的配置文件，通过 USB 等方式传输到本机上。

从 [geoip](https://github.com/Loyalsoldier/geoip) 项目中，可以获得 `Country.mmdb` 文件，将其放置到 `~/.config/clash` 目录下。

对于 `clash` 来说，dashboard 不是必需的。
如果需要，可以使用公共的 dashboard，例如：<http://clash.razord.top>、<http://yacd.haishan.me>。
也可以使用本地部署的 dashboard，例如 [yacd](https://github.com/haishanh/yacd)，根据项目的说明操作，部署本地服务。
或者，将下载的项目文件放置到合适的路径下，并在 `clash` 的配置文件中添加：

```
external-controller: 0.0.0.0:9090
external-ui: /path/to/dashboard/project
secret: 123123
```

其中，`secret` 是可选的密码。在启动 `clash` 后，通过 <http://127.0.0.1:9090/ui> 地址，即可访问 dashboard。

将 `clash` 注册为系统服务，可以创建 `/etc/systemd/system/clash.service` 文件，内容如下：

```
[Unit]
Description=Clash daemon, A rule-based proxy in Go.
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/clash # 根据需要添加参数

[Install]
WantedBy=multi-user.target
```

然后，使用以下命令，管理 `clash` 服务：

```
sudo systemctl enable --now clash
sudo systemctl stop clash
sudo systemctl status clash
```

#### 2.3.2 设置系统代理

通过设置环境变量的方法，可以设置系统代理。具体细节可以参考：[Environment variables](https://wiki.archlinux.org/title/Environment_variables)、[Proxy server](https://wiki.archlinux.org/title/Proxy_server)。

例如，可以在 `~/.zprofile` 文件中，添加以下内容：

```
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export all_proxy="socks5://127.0.0.1:7890"
```

要取消设置系统代理，可以使用以下命令：

```
unset http_proxy
unset https_proxy
unset all_proxy
```

需要注意的是，这种取消方法只在当前终端会话中有效。
如果需要永久取消设置系统代理，可以移除或注释 `~/.zprofile` 文件中的相关内容，并重新登录。

为了更方便地管理系统代理，在 [dotfiles](https://github.com/peoxin/dotfiles) 中编写了相关脚本，可供参考。

#### 2.3.3 安装 `clash-verge-rev-bin`

`clash-verge-rev-bin` 软件包位于 AUR 中。因为此时无法直接访问 AUR，所以参考 [Arch User Repository](https://wiki.archlinux.org/title/Arch_User_Repository)，可以采用以下方法：

- 在其他设备上下载该软件包的构建文件，然后通过 USB 等方式传输到本机上；
- 使用 GitHub 上的只读镜像 [aur on GitHub](https://github.com/archlinux/aur)。使用以下命令获得软件包的构建文件，并进行构建和安装：

```
git clone --branch package_name --single-branch https://github.com/archlinux/aur.git package_name
cd package_name && makepkg -si
```

需要注意的是，在这一过程中，可能会依赖对于 GitHub 等网站的访问，所以需要提前解决访问 GitHub 的问题。

#### 2.3.4 其他细节

测试能否连接外网，可以使用以下命令：

```
curl https://www.google.com
```

如果遇到代理无法正常使用的问题，尝试更新系统时间。以下命令可以自动同步系统时间：

```
sudo timedatectl set-ntp true
```

## 3 安装 AUR 助手

AUR 助手可以帮助用户更方便地安装和管理软件包，包括 AUR 中的软件包。
使用 AUR 助手后，可以不用再手动下载和构建 AUR 软件包，而是使用类似于 `pacman` 的命令进行安装。

AUR 助手本身，也是 AUR 中的软件包，需要通过手动构建的方式进行安装。
根据 [AUR helpers](https://wiki.archlinux.org/title/AUR_helpers) 中的说明，有多种 AUR 助手可供选择。
下面以 `paru` 为例，演示安装方法：

```
git clone https://aur.archlinux.org/paru.git
cd paru && makepkg -si
```

安装完成后，使用 `paru` 代替原来的 `pacman`，即可使用 AUR 助手。

## 4 输入法配置

首先，安装输入法框架 `fcitx5`:

```
sudo pacman -S fcitx5-im
```

然后，设置环境变量：

```
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export SDL_IM_MODULE=fcitx
export GLFW_IM_MODULE=ibus
export XMODIFIERS=@im=fcitx
```

最后，安装输入法引擎和输入法。主要有两种选择：

- fcitx5-chinese-addons

```
sudo pacman -S fcitx5-chinese-addons
```

- rime

```
sudo pacman -S fcitx5-rime

# 以下输入法选择其一即可
sudo pacman -S rime-double-pinyin
paru -S rime-flypy
paru -S rime-ice-git
```

此外，安装 `catppuccin` 主题：

```
cd ~/.local/share/fcitx5
git clone https://github.com/catppuccin/fcitx5.git catppuccin
mv catppuccin/src themes && rm -rf catppuccin
```

## 5 安装显卡驱动

如果没有使用独立显卡，可以跳过这一步。

如果使用 NVIDIA 显卡，参考 [NVIDIA - ArchWiki](https://wiki.archlinux.org/title/NVIDIA) 和 [NVidia - Hyprland](https://wiki.hyprland.org/Nvidia) 来安装驱动。对于 Turing 架构及更新的显卡，可以安装以下软件包：

```
sudo pacman -S nvidia-open-dkms nvidia-utils lib32-nvidia-utils egl-wayland
sudo pacman -S dkms linux-headers
```

然后，编辑 `/etc/mkinitcpio.conf` 文件，将以下内容添加到 `MODULES=()` 中：

```
MODULES=(... nvidia nvidia_modeset nvidia_uvm nvidia_drm ...)
```

此外，还需要将 `HOOKS` 列表中的 `kms` 移除。然后，创建 `/etc/modprobe.d/nvidia.conf` 文件，添加以下内容：

```
options nvidia_drm modeset=1 fbdev=1
```

最后，重新生成 `initramfs` 并重启系统：

```
sudo mkinitcpio -P
```
