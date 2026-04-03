#import "../../config.typ": post
#show: post.with(
  title: "rEFInd 的安装和配置",
  pub-date: datetime(year: 2025, month: 1, day: 6),
  mod-date: datetime(year: 2025, month: 1, day: 6),
)

= rEFInd 的安装和配置

#link("https://www.rodsbooks.com/refind")[rEFInd] 是一个图形化的 UEFI 引导管理器，支持多种操作系统的启动引导。它可以自动检测 EFI 引导项，因此特别适合于使用 Linux to Go 的情况。

下面介绍其安装和配置方法。

== 1 Arch Linux 下的安装

安装 `refind` 软件包，并运行自动化安装脚本：

```
sudo pacman -S refind
sudo refind-install
```

执行上述命令后，会将 rEFInd 文件复制到 EFI 分区的 `EFI/refind` 目录下，并使用 `efibootmgr` 工具将 rEFInd 设置成默认的 EFI 启动项。

== 2 Windows 下的安装

首先，从 #link("https://www.rodsbooks.com/refind/getting.html")[Getting rEFInd] 下载 rEFInd 的安装包。

然后，使用 DiskGenius 工具，将安装包内的 `refind` 目录，拷贝到 ESP 分区的 `EFI` 目录下。然后，删除 `refind` 目录下与本机架构无关的内容，并将 `refind.conf-sample` 重命名为 `refind.conf`。

最后，使用 Bootice 或 DiskGenius 工具，将 rEFInd 的引导文件 `\EFI\refind\refind_x64.efi` 添加到 UEFI 启动项列表中，并将其上移至第一位。如果上述操作无效，那么可以尝试在计算机的 BIOS 中进行设置。

== 3 配置主题

以下配置 #link("https://github.com/catppuccin/refind")[Catppuccin] 主题。首先，下载主题文件：

```
cd /boot/EFI/refind
mkdir themes
git clone https://github.com/catppuccin/refind.git themes/catppuccin
```

然后，将以下内容添加到 `refind.conf` 文件的末尾：

```
include themes/catppuccin/macchiato.conf
```

此外，可以根据需要修改主题配置文件。建议取消隐藏 `label`。
