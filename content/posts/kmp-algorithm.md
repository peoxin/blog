---
title: KMP 算法
date: 2023-03-08T17:52:36+08:00
draft: true
---

如何在字符串 S 中查找模式串 P 是否存在？

一种简单的想法是进行蛮力匹配（Brute-Force）。使用两层循环查找模式串是否存在：外层循环移动模式串的位置，内层循环对字符串和模式串的对应字符进行比较。

相较于蛮力匹配，使用 KMP 算法可以提高匹配效率。

## 算法要点

推荐 KMP 算法讲解视频：[最浅显易懂的 KMP 算法讲解](https://www.bilibili.com/video/BV1AY4y157yL)

KMP 算法的关键在于构建 next 数组，需要注意：

- 在 next 数组中，`next[j]` 存储的是之前的子串（不包含 `P[j]`）中，最长匹配前后缀的长度。因为索引从 0 开始，所以在 KMP 匹配时，模式串指针可以跳转到最长匹配前缀的结尾下一处。

- 在构建 next 数组时，使用了递推的方法。在求取 `next[j]` 时，不仅要关注 `P[j-1]` 和 `P[t-1]` 是否相同，还可以关注 `P[j]` 和 `P[t]` 是否不同。因为如果 `P[j]` 和 `P[t]` 相同，则模式串指针移动前后指向的字符相同，匹配仍会失败。
- 检查在特殊情况下，算法实现是否正确。例如，`next[0]` 和 `next[1]` 是否计算正确。

## 实现代码

### 搜索第一个匹配项

搜索模式串 P 在字符串 S 中是否出现。如果出现，返回第一个匹配项的下标；否则，返回 -1。

```c++
int *build_next(char *P) {
    int m = strlen(P); // 模式串 P 的长度
    int *next = new int[m];
    next[0] = -1;
    int j = 0; // 主指针
    int t = -1; // 当前最长匹配前缀的结尾下一处指针

    while (j < m - 1) {
        if (t < 0 || P[j] == P[t]) {
            ++j;
            ++t;
            next[j] = (P[j] != P[t]? t : next[t]);
        } else {
            t = next[t];
        }
    }
    return next;
}

int kmp_match(char *S, char *P) {
    int *next = build_next(P);
    int n = strlen(S); // 字符串 S 的长度
    int m = strlen(P); // 模式串 P 的长度
    int i = 0; // 字符串 S 的指针
    int j = 0; // 模式串 P 的指针

    while (j < m && i < n) {
        if (j < 0 || S[i] == P[j]) {
            ++i;
            ++j;
        } else {
            j = next[j];
        }
    }
    delete [] next;
    return j == m? i - j : -1;
}
```

### 搜索全部匹配项

搜索模式串 P 在字符串 S 中出现的全部位置。

```c++
int *build_next(char *P) {
    int m = strlen(P); // 模式串 P 的长度
    int *next = new int[m + 1];
    next[0] = -1;
    int j = 0; // 主指针
    int t = -1; // 当前最长匹配前缀的结尾下一处指针

    while (j < m) {
        if (t < 0 || P[j] == P[t]) {
            ++j;
            ++t;
            next[j] = ((j == m || P[j] != P[t])? t : next[t]);
        } else {
            t = next[t];
        }
    }
    return next;
}

std::vector<int> kmp_match(char *S, char *P) {
    int *next = build_next(P);
    std::vector<int> pos; // 记录所有匹配项的位置
    int n = strlen(S); // 字符串 S 的长度
    int m = strlen(P); // 模式串 P 的长度
    int i = 0; // 字符串 S 的指针
    int j = 0; // 模式串 P 的指针

    while (i < n) {
        if (j < 0 || S[i] == P[j]) {
            ++i;
            ++j;
            if (j == m) {
                pos.push_back(i - j);
                j = next[j];
            }
        } else {
            j = next[j];
        }
    }
    delete [] next;
    return pos;
}
```
