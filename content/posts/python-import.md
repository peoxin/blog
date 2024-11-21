---
title: Python 解决导入问题
date: 2024-11-11T16:38:30+08:00
categories: ["python"]
tags: ["python"]
draft: false
---

在使用 Python 编写程序时，如果项目结构比较复杂，那么不同模块之间的导入就可能遇到各种问题。
为了解决这些问题，首先阅读 Python 官方文档中对于导入系统的介绍，理解其基本规则，然后尝试给出几种较好的实践方案。

## 1 官方文档

在 Python 的官方文档中，对于 [导入系统 The import system](https://docs.python.org/3/reference/import.html) 进行了详细的介绍。
但是，官方文档中的介绍比较长，因此以下摘录其中的要点。

### 1.1 [Module 和 Package](https://docs.python.org/3/reference/import.html#packages)

> Python has only one type of [module](https://docs.python.org/3/glossary.html#term-module) object, and all modules are of this type, regardless of whether the module is implemented in Python, C, or something else.
> To help organize modules and provide a naming hierarchy, Python has a concept of [packages](https://docs.python.org/3/glossary.html#term-package).

在 Python 语言中，所有模块 (Module) 都属于同一种类型，无论该模块是用 Python、C 还是其他方式实现的。
为了更方便地组织模块，Python 引入了包 (Package) 的概念。

> You can think of packages as the directories on a file system and modules as files within directories, but don’t take this analogy too literally since packages and modules need not originate from the file system.

为了便于理解，可以近似地将 package 看作是文件系统上的目录，将 module 看作是目录中的文件。

> It’s important to keep in mind that all packages are modules, but not all modules are packages.
> Or put another way, packages are just a special kind of module.
> Specifically, any module that contains a `__path__` attribute is considered a package.

所有 package 都是 module，但并非所有 module 都是 package。换句话说，package 是一种特殊的 module。
具体来说，任何包含 `__path__` 属性的 module 都被视为一个 package。

> Python defines two types of packages, regular packages and namespace packages.
> Regular packages are traditional packages as they existed in Python 3.2 and earlier.
> A regular package is typically implemented as a directory containing an `__init__.py` file.
> When a regular package is imported, this `__init__.py` file is implicitly executed, and the objects it defines are bound to names in the package’s namespace.
> The `__init__.py` file can contain the same Python code that any other module can contain, and Python will add some additional attributes to the module when it is imported.

在 Python 语言中，定义了两种类型的包，即常规包 (Regular package) 和命名空间包 (Namespace package)。
常规包通常实现为包含 `__init__.py` 文件的目录。在导入常规包时，该 `__init__.py` 文件将被隐式执行。

> A package’s `__init__.py` file may set or alter the package’s `__path__` attribute, and this was typically the way namespace packages were implemented prior to [PEP 420](https://peps.python.org/pep-0420).
> With the adoption of PEP 420, namespace packages no longer need to supply `__init__.py` files containing only `__path__` manipulation code; the import machinery automatically sets **path** correctly for the namespace package.

在实现 package 的目录下，`__init__.py` 文件可以设置或更改 package 的 `__path__` 属性。
在 `__init__.py` 文件为空的情况下，package 的 `__path__` 属性也能被自动设置。

### 1.2 基于路径的导入

> Python includes a number of default finders and importers.
> The first one knows how to locate built-in modules, and the second knows how to locate frozen modules.
> A third default finder searches an [import path](https://docs.python.org/3/glossary.html#term-import-path) for modules.
> The import path is a list of locations that may name file system paths or zip files.

在 Python 的导入系统中，包含着许多默认的查找器和导入器。
其中，第三个默认查找器在导入路径中搜索模块。

> [sys.path](https://docs.python.org/3/library/sys.html#sys.path) contains a list of strings providing search locations for modules and packages.
>
> During import, this list of locations usually comes from `sys.path`, but for subpackages it may also come from the parent package’s `__path__` attribute.

sys.path 包含一个字符串列表，用于提供模块和包的搜索位置。
在导入过程中，导入路径的列表通常来自 `sys.path`。但对于子包，它也可能来自父包的 `__path__` 属性。

> By default, as initialized upon program startup, a potentially unsafe path is prepended to `sys.path` (before the entries inserted as a result of `PYTHONPATH`):
>
> - [`python -m module`](https://docs.python.org/3/using/cmdline.html#cmdoption-m) command line: prepend the current working directory.
> - `python script.py` command line: prepend the script’s directory. If it’s a symbolic link, resolve symbolic links.
> - `python -c code` and `python` (REPL) command lines: prepend an empty string, which means the current working directory.
>
> A program is free to modify this list for its own purposes.
> Only strings should be added to `sys.path`; all other data types are ignored during import.

默认情况下，在程序初始化时，会将以下路径添加到 `sys.path` 列表的最前面：

- `python -m module` 命令行：添加当前工作目录。
- `python script.py` 命令行：添加脚本所在的目录。
- `python -c code` 和 `python` (REPL) 命令行：添加一个空字符串，表示当前工作目录。

### 1.3 [相对导入](https://docs.python.org/3/reference/import.html#package-relative-imports)

> Relative imports use leading dots.
> A single leading dot indicates a relative import, starting with the current package.
> Two or more leading dots indicate a relative import to the parent(s) of the current package, one level per dot after the first.

相对导入必须使用 `from . import` 格式的语法。例如：

```
from . import moduleY
from .moduleY import spam
from ..subpackage1 import moduleY
```

> [Intra-package References](https://docs.python.org/3/tutorial/modules.html#intra-package-references):
>
> Note that relative imports are based on the name of the current module.
> Since the name of the main module is always `__main__`, modules intended for use as the main module of a Python application must always use absolute imports.

相对导入基于当前模块的名称，即 `__name__` 属性。
由于主模块（即通过命令行运行的文件）的名称始终为 `__main__`，不包含层次关系信息，因此在主模块的内部只能使用绝对导入。

## 2 实践方案

### 2.1 手动修改 `sys.path`

在 `__init__.py` 或者其他需要的文件中，添加所需的导入路径到 `sys.path`。例如：

```python
import sys
from pathlib import Path

parents_dir = Path(__file__).resolve().parents[0:2]
for parent_dir in parents_dir:
    if parent_dir not in sys.path:
        sys.path.insert(0, str(parent_dir))
```

这种方案可能不太优雅，但却很灵活。对于具有复杂导入关系的项目，可以考虑这种方案。
在使用这种方案时，建议全部使用绝对引用，而不再使用相对引用。
