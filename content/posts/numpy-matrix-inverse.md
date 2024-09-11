---
title: Numpy 矩阵求逆
date: 2023-03-07T01:03:38+08:00
draft: true
---


在 Numpy 中，对于 `ndarray` 和 `matrix` 对象，求解逆矩阵的方法不同。

## numpy.ndarray

矩阵求逆：`numpy.linalg.inv()`

对于 `ndarray` 对象，求解逆矩阵不能使用 `A**(-1)`，其结果是对矩阵 A 中的每个元素求倒数。

矩阵求伪逆：`numpy.linalg.pinv()`

> 矩阵 A 的伪逆（pseudo-inverse）为：$(A^TA)^{-1}A^T$

## numpy.matrix

矩阵求逆有三种方法：

- `numpy.linalg.inv()`

- `A.I`
- `A**(-1)`

矩阵求伪逆：`numpy.linalg.pinv()`