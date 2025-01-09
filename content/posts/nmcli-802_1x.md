---
title: 使用 nmcli 连接 802.1x 网络
date: 2025-01-09T22:37:25+08:00
categories: ["linux"]
tags: ["network", linux"]
draft: false
---

在 Linux 系统中，使用 NetworkManager 的 `nmcli` 命令行工具，可以连接 802.1x 网络。

以下是连接校园网的命令，可以作为参考：

```
# DEVICE_NAME 为无线网卡的设备名称，可以通过 `nmcli device` 或 `ip link` 命令查看
# WIFI_SSID 为无线网络的 SSID
# USERNAME 为用户名
nmcli connection add \
    type wifi \
    ifname DEVICE_NAME \
    con-name WIFI_SSID \
    ssid WIFI_SSID -- \
    wifi-sec.key-mgmt wpa-eap \
    802-1x.eap peap \
    802-1x.phase1-auth-flags tls-1-0-enable \
    802-1x.phase2-auth mschapv2 \
    802-1x.identity USERNAME

nmcli --ask connection up WIFI_SSID
```
