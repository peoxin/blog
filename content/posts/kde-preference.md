---
title: KDE Plasma 偏好设置
date: 2022-09-03T22:54:40+08:00
categories: ["linux"]
tags: ["KDE", "linux"]
draft: false
---

> 本文中所进行的偏好设置，可能不适用于最新的 KDE Plasma 6。

## 1 桌面布局

### 1.1 布局

使用 latte-dock 的自定义 Layout 进行桌面布局。

Layout 文件：[peoxin/dotfiles](https://github.com/peoxin/dotfiles)

### 1.2 小部件设置

#### Window Title Applet

Behavior > Placeholder：关闭 Show activity information

#### Better Inline Clock

Appearance > Information：关闭 Show Separator

Appearance > Information：Use fixed font size

Appearance > Date format：MM-dd ddd

#### 系统监视传感器

外观 > 标题：CPU | RAM

外观 > 显示样式：水平柱状图

传感器详情 > 传感器：CPU总使用率 `#008baa` | 已用物理内存百分比 `#71aa00`

#### 应用程序启动器

常规 > 图标：app-launcher 或 start-here

## 2 系统设置

### 2.1 外观

全局主题：Arc Dark

应用程序风格：Breeze 微风（不透明度 80%）

Plasma 视觉风格：Arc Dark

窗口装饰元素：Arc Dark

颜色：Arc Dark

字体：Noto Sans CJK SC、Noto Sans Mono

图标：Papirus-Dark

光标：Breeze 微风

欢迎屏幕：Arc Dark

### 2.2 工作区行为

#### 常规行为

单击文件、文件夹时：选中

#### 屏幕边缘

左下角：桌面概览

右下角：显示桌面

### 2.3 窗口管理

#### 任务切换器

主窗口 > 可视化：显示选中窗口

主窗口 > 可视化：信息

### 2.4 搜索

#### 网页搜索关键字

关键字分隔符：空格

### 2.5 语言和区域设置

#### 输入法

输入法关闭：英语 - 美国

全局选项 > 向前切换输入法：<kbd>Alt</kbd> + <kbd>左Shift</kbd>

全局选项 > 向后切换输入法：<kbd>Alt</kbd> + <kbd>右Shift</kbd>

全局选项 > 向前切换输入法分组：删除

全局选项 > 向后切换输入法分组：删除

全局选项 > 激活输入法：删除

全局选项 > 取消激活输入法：删除

附加组件 > 经典用户界面 > 主题：KDE Plasma

双拼 > 标点 > 项目：按键 <kbd>/</kbd> 映射到标点 <kbd>、</kbd>

双拼 > 快速输入的触发键：<kbd>\\</kbd>

### 2.6 输入设备

#### 键盘

高级 > CapsLock 行为：将 <kbd>CapsLock</kbd> 作为额外的 <kbd>Esc</kbd>，<kbd>Shift</kbd> + <kbd>CapsLock</kbd> 作为 <kbd>Compose</kbd>

#### 触摸板

滚动：反向滚动
