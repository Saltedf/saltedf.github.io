# 基本的 cmake 命令

## 配置阶段:生成 makefile

`cmake -B build -D CMAKE_CXX_COMPILER=clang++`

    -B 指定cmake的输出路径,并会自动创建build目录
    -DCMAKE_CXX_COMPILER=xxx 指定cmake所用的C++编译器
    -DCMAKE_BUILD_TYPE=Release/Dehug

    -G Ninja/"Unix Makefiles" 指定构建系统

## 实际构建阶段:执行 makefile

自动识别构建工具,并在 build 目录中进行构建(make -j4)

`cmake --build build -j4`

# 为目标添加源码文件

```cmake
add_executable(myexe)
set(myexe_sources main.cc file1.cc file2.cc )
target_sources(myexe ${myexe_sources} )
```

# 生成库

    add_library(mylib STATIC  source1.cc source2.cc)
    add_library(mylib SHARED source1.cc source2.cc)

反汇编显示带有 plt 字样的函数表示插桩函数, 其真正的实现不在当前文件中,
而是在动态库中(共享库)

# 为某个可执行文件链接上库

    target_link_libraries(myexe PUBLIC mylib)

# extern "C" {}

在 C++代码中将某段代码解释为 C 语言的, 从而避免使用重载机制

```cpp
#ifdef __cplusplus
extern "C" {
#endif

// 期望被理解为C语言的代码

#ifdef __cplusplus
}
#endif
```

# pragma once / ifndef define endif

# 为某个目标指定头文件搜索目录

    target_include_directories(mylib PUBLIC ..XX)

PUBLIC/PRIVATE 的作用是是否将这个属性(这里是头文件搜索路径)也传递给使用此库/目标的其它目标

对可执行文件这样的目标来说, PUBLIC 的标识没太多意义.

# 为某个目标添加宏定义

    target_add_definitions(myexe PUBLIC MY_MACRO=XX )

# 为某目标添加编译选项

    target_compile_options(myexe PUBLIC -fopenmp

# 全局添加宏定义

    add_definitions()

# 每个 CMakeLists 的第二行: project()

```cmake
project(MyProject VERSION 1.0.0
                  DESCRIPITOIN "this is my project"
          LANGUAGES CXX )

```

首个参数是项目的名称. 语言默认是 `C CXX` , 即 c 和 C++

# 局部变量

## 定义变量

    set(MY_VAR "value" )

## 访问一个变量:

    ${MY_VAR}

cmake 中有作用域的概念,
这意味着一个定义在函数范围内/子目录的一个文件范围内的变量在范围外是无法访问的.

## 可以用 `set()` 定义一个 list

    set(MY_LIST "first" "second" ) # 元素用空格分割
    set(MY_LIST "first;second" ) # 这种方式也是等价的, 用分号.

用 `${}`
去使用变量时其实是以替换的方式来"展开"变量名.因此在使用表示路径的变量时要额外在外面加一层引号:

`"${MY_PATH}"` 不要用 `${MY_PATH}` ,
否则一旦有含空格的路径时就会被当成 list 进行处理, 而不是当成一个整体.
因此使用路径变量时一定要加上双引号.
