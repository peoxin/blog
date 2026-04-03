#import "../../config.typ": post
#show: post.with(
  title: "Numpy 矩阵求逆",
  pub-date: datetime(year: 2023, month: 3, day: 7),
  mod-date: datetime(year: 2023, month: 3, day: 7),
)

= Numpy 矩阵求逆

在 Numpy 中，对于 `ndarray` 和 `matrix` 对象，求解逆矩阵的方法不同。

== numpy.ndarray

矩阵求逆：`numpy.linalg.inv()`

对于 `ndarray` 对象，求解逆矩阵不能使用 `A**(-1)`，其结果是对矩阵 A 中的每个元素求倒数。

== numpy.matrix

矩阵求逆有三种方法：

- `numpy.linalg.inv()`

- `A.I`
- `A**(-1)`
