---
title: Seafile CLI 同步清华云盘
date: 2025-01-10T20:06:02+08:00
categories: ["linux"]
tags: ["seafile", "linux"]
draft: false
---

Seafile CLI 的详细使用方法，可以参考官方文档 [Seafile client for a Cli server](https://help.seafile.com/syncing_client/linux-cli)。

下面介绍如何使用 Seafile CLI 同步清华云盘：

```sh
# LIBRARY_ID 为资料库 ID
# THU_NUMBER_ID 为清华大学学号（数字）
# TOKEN 为清华云盘的 API Token
# 清华云盘网站 Cookie 中的 seahub_auth 字段，其格式为 THU_NUMBER_ID@tsinghua.edu.cn@TOKEN
seaf-cli sync \
    -s https://cloud.tsinghua.edu.cn \
    -l LIBRARY_ID \
    -d /path/to/sync \
    -u THU_NUMBER_ID@tsinghua.edu.cn \
    -T TOKEN
```
