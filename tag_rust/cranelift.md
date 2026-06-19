# [Cranelift IR 文档](https://docs.rs/cranelift-codegen/latest/cranelift_codegen/ir/trait.InstBuilder.html)

ir主要有两种形式,
一种是在内存中的数据结构形式.另一种是用于测试&debug的文本形式,
其文件拓展名为 `.clif` .

## 结构一览

cranelift独立地编译函数. 一个ir文件可能包含了多个函数,
编程API可同时创建多个函数句柄,
但函数之间不共享任何数据,也不直接互相引用.

这是一个计算浮点数的平均值的C函数:

``` c
float
average(const float *array, size_t count)
{
  double sum = 0;
  for (size_t i = 0; i < count; i++)
    sum += array[i];
  return sum / count;
}
```

下面是编译为ir形式的同一函数:

函数定义的第一行提供了函数名和函数签名, 它声明参数类型和返回类型.
接下来是"函数前言"function peamble,
它声明了一些可以在函数内部引用的元素, 在这个例子中,
函数前言中声明了一个显式的stack slot : `ss0` .

在函数前言之后是函数体, 它是由扩展基本块(EBB)组成的, 首个EBB是
"入口块"(entry block). 每个EBB以一个 **终结指令(terminator
instruction)** 结束. 就因此如果没有明确的分支指令,
则执行流永远不会进入下个EBB.

``` asm
test verifier

function %average(i32, i32) -> f32 system_v {
    ss0 = explicit_slot 8 ; Stack slot for `sum`.

block1(v0: i32, v1: i32):
    v2 = f64const 0x0.0
    stack_store v2, ss0
    brz v1, block5  ; Handle count == 0.
    jump block2

block2:
    v3 = iconst.i32 0 ;<<== i的初值0 
    jump block3(v3)

block3(v4: i32):  ; <<== v4 本次迭代中的 i 
    v5 = imul_imm v4, 4
    v6 = iadd v0, v5
    v7 = load.f32 v6  ; array[i]
    v8 = fpromote.f64 v7
    v9 = stack_load.f64 ss0
    v10 = fadd v8, v9
    stack_store v10, ss0
    v11 = iadd_imm v4, 1 ;<<== v11 i++ 更新i
    v12 = icmp ult v11, v1
    brnz v12, block3(v11) ; Loop backedge.
    jump block4

block4:
    v13 = stack_load.f64 ss0
    v14 = fcvt_from_uint.f64 v1
    v15 = fdiv v13, v14
    v16 = fdemote.f32 v15
    return v16

block5:
    v100 = f32const +NaN
    return v100
}
```

一个 `.clif` 文件是由一系列独立的函数定义组成的:

``` asm
function_list : { function }

function : "function" function_name signature "{" preamble function_body "}"

preamble : { preamble_decl }

function_body : { extended_basic_block }
```

### 静态单赋值形式 SSA form

在函数体中的指令使用并产生ssa形式的 **值** .
这意味着每个值仅能恰好被定义一次, 每处对值的使用都必须受定义支配.

Cranelift 没有使用phi指令, 但使用了 **EBB参数**.
可以用一个有类型参数的list 定义一个EBB. 每当控制流被转移到一个EBB时,
必须提供EBB的实参. 当进入一个函数时, 函数的入参被作为入口EBB的参数传入.

指令定义零个,一个,或多个 结果值. 任何SSA值不是EBB参数就是指令结果值.

在上面的例子中, 循环归纳变量 `i` 被表示为三个SSA值: 在block2,
v3是其初始值; 在循环块block3中, EBB参数v4代表每次迭代中的 `i` 的值;
最后, v11被计算为下次迭代中使用的 `i` 的值.

`cranelift_frontend`
中包含了将包含了对统一变量多次赋值的程序翻译为SSA形式IR的工具.
这些变量也可以被表示为 `stack slot` , 它亦可通过 `stack_store` 和
`stack_load` 进行访问. 并且可以用 `stack_addr` 取得它们的地址,
就像类C编程语言那样, 支持取得局部变量的地址.

## 值的类型

## 控制流

## 函数调用

## 内存

## ISA特定指令

## 代码生成实现指令

## 指令组

## 实现限制

## 一些名词说明

### 陷入trap/traps/trapping :

终止当前线程的执行. 陷入后的具体行为取决于OS.
例如一个常见的行为是传递signal,具体的信号要取决与触发它的事件.

### 可寻址addressable

### 可访问accessible

### 终止指令terminator instruction :

一个控制流指令, 它 **无条件** 地将执行流导向其它地方.
永远不会继续执行终止指令后的指令.

基本的终止指令有: `br` , `return` , `trap`.
这些有条件陷入的条件分支和条件指令 **不是** 终止指令.

### stack slot:

在当前函数的活跃栈帧中的一块固定大小的内存分配. 它有两种: explicit stack
slot 和 spill stack slot

### 显式的stack slot:

在当前函数的活跃栈帧中的一块固定大小的内存分配. 它与spill stack
slot的不同在于,它可被前端创建, 并且可能会占用地址.

### spill stack slot :

在当前函数的活跃栈帧中的一块固定大小的内存分配.它和explicit stack slot
的不同之处是, 它们仅在寄存器分配期间被创建, 并且可能不会占用地址.

### 中间表示 IR :

用于描述函数的语言.

### function body:

包含了函数中的所有可执行代码的基本扩展块.函数体紧接 function peamble
之后.

### function preamble :

可用在函数体中的实体的声明列表. 可以在preamble中声明的实体有:

- stack slots
- 可直接调用的函数
- 非直接调用函数的函数签名
- 不属于签名的一部分的函数flags和属性

### 函数签名:

函数签名描述了如何调用一个函数. 它有以下部分组成:

- 调用约定
- 参数的数量和返回值(函数能返回多个值)
- 每个参数的类型和flags
- 每个返回值的类型和flags

不是所有函数属性都是签名的一部分, 例如, 一个从不返回的函数被标记为
\`noreturn\` , 但这点对于调用来讲是没必要知道的. 因此它仅仅是一个属性,
但不是签名的一部分.

### 基本块 basic block

### 入口块 entry block

### EBB

### EBB形参

### EBB实参

# reader: 解析 `.clif` 文件的测试模块
