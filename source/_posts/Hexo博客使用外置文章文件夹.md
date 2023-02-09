---
title: Hexo博客使用外置文章文件夹
date: 2022-08-23 22:43:59
categories:
  - blog
tags:
  - hexo
  - blog
index_img: 
excerpt: 将Hexo博客的文章，保存在外置的文件夹中，便于管理和备份
---

将Hexo博客的文章，保存在外置的文件夹中，便于管理和备份。

Hexo博客文件夹：

```text
hexo-blog
└─ source
   ├─ _posts
   └─ images
```

外置文章文件夹：

```text
blog-posts
└─ images
```

符号链接：

```text
hexo-blog/source/_posts -> blog-posts
hexo-blog/source/images -> blog-posts/images
```

博客文章保存在`blog-posts`文件夹下。图片保存在`blog-posts/images`文件夹下，使用相对路径引用图片。

`hexo-blog/source`和`blog-posts`路径下的`images`文件夹必须同名。