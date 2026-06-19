# 语义分析 sematic analysis

在语义分析阶段我们要进行一些上下文相关的分析. 例:

1.  检查是否所有标识符在使用之前都有声明.
2.  类型检查

## Scope定义

scope 是规定了标识符在程序中可访问的范围. 多个scope之间是互不相交的.

例如, 下面有两个作用域, 一个是for
loop之内的.另外一个是除了for循环体之外的函数体.

    void fun(int n) {
      int a;              // scope 1

      for(n = 0;n<10;n++){//===
        int a = n*n;      //  |===>  scope 2 
        printf("%d\n",a); //===
      }
              // scope 1
    }

## Static Scope VS Dynamic Scope

大多数语言采用静态作用域, 即作用域只依赖程序的文本, 而不是运行时的行为.
动态作用域则相反, 作用域依赖于程序运行时的行为.

    void foo(int x) {
      int a = 3;
      bar(3);  // 对于动态语言, eg:早期的lisp, 此处将成功打印出3. 
    }

    void bar(int y){
      printf("%d", a); // 而对于像C这样的static scope语言, 这里显然无法通过编译. 
    }

例, C语言中的标识符绑定被下面的东西引入:

- 函数定义 function definitons
- struct definitions
- variable definitions
- struct中字段的定义.
- 函数参数的声明

虽然大多数标识符满足最近嵌套作用域原则. 但仍有例外:

1.  C++ 中的成员函数可以在class之外定义.
    但在这些函数的定义中仍然能访问class成员.
2.  C++ 中的向前forward声明, 使得 前面定义的类可以引用定义在后面的类.

## 通过在AST上进行递归下降进行语义分析

在C中,block就是最常见的作用域scope. 在早期的C中,
一个scope中的变量声明必须全都放在开头,之后才能使用变量. AST结构如下:


              代码块
           /         \
     声明list       语句list
     /  |  \       /   |   \
    d1  d2  d3    s1   s2  s3 

而现在的C语言允许声明和普通语句混合:


          代码块
           /       
      代码块项目list 
      /    |     \     \ 
    语句1 声明1  语句2  声明2 .. 

每当进入一个scope / 代码块
,就会创建一个用来保存变量声明/定义的上下文context.
而每当离开一个scope时, 相应的上下文就会被销毁.

这种context是什么?

### 符号表 symbol table

之所以叫做符号表,而不是"字符串"表, 是因为这个表的key不单单是一个字符串.
字符串在计算hash值, 测试相等性,
比较两个字符串的大小上是低效的.(线性时间,因为要遍历每个字符)

因此要创建一个符号类型, 并用它作为key.这样的表叫做符号表.

每当进入一个新的作用域时,
将当前的符号表复制一份作为当前scope的符号表.并将旧的保存下来.
每当下面遇到一个声明, 将其添加到符号表.

当离开一个scope后, 将保存的符号表恢复为当前符号表.

1.  用符号表实现"环境"

    使用存放scope(符号表)的 **Stack**

        enter_scope(): 创建并push一个新的scope 
        exit_scope(): 离开pop当前scope

        find_symbol(x): 从栈顶的scope中开始寻找符号x
        add_symbol(x): 将符号x加入当前的(栈顶)scope
        check_scope(x): 检查x是否在当前(栈顶)scope中存在定义, 用于防止在同一scope发生重定义

    例如在C++这样的语言中,
    可以先使用一个未定义但已经声明的标识符.(class的forward声明),
    将其具体定义写在使用处的后面.
    因此这样的语法无法通过遍历一次AST就能解析完所有的符号使用.因此至少需要两次遍历:
    第一遍, 收集所有scope中的 **声明** 第二遍, 用符号表来解析使用.

# 活动记录 AR

## 理论动机

所谓函数是一段代码, 位于代码段, 是只读的.
但是每个函数被调用时都包含着对应当前实例的特有数据: 入参, 局部变量,
中间结果 … 这些数据是运行时动态创建的, 不能放在代码段中.
因此需要有某种数据结构来管理每个函数调用对应的特有数据.这种结构就是栈stack.

一门语言中的函数的语法决定了如何实现函数调用.
比较复杂的函数实现就是所谓的高阶函数: 入参和返回值都可以是函数.
并且为了支持能够返回一个函数对象, 语法也必须支持嵌套的函数定义.
这些函数的特性增加了实现的难度:

``` ocaml
let myfunc x = 
  let
    bar y = x + y 
  in 
  bar 
;;
```

``` ocaml
# let bar =myfunc 2 ;;
val bar : int -> int = <fun>
```

为了实现上的简单, 暂时不考虑返回一个函数对象的情况. 仅允许嵌套函数定义.

这里的栈不是标准的栈 – 仅支持push/pop/peek. 因为要访问变量,
因此要实现为数组.并用一个指针来标记栈顶, 即栈指针sp.
这个数组是从高地址向低地址方向生长的.就像山洞中的钟乳石.

存放于栈的每个函数调用对应的特有数据被称为一个frame.
一个栈帧中通常包含这些部分:
入参,函数内声明的局部变量,返回地址,计算的中间结果,保存的寄存器.

某些局部变量不放在寄存器中, 而是存放于stack中,
这些被占用的寄存器可能会与该函数调用的其他函数相冲突.
因此需要将其保存栈中.

``` c
int foo(int x , int y)
{
  int temp = x + 1;
  int temp2 = x - y ;
  return temp * temp2 ;
}
```

``` asm
foo:                                    # -O0
        pushq   %rbp            # 保存帧指针 
        movq    %rsp, %rbp      # 
        movl    %edi, -4(%rbp)  # x
        movl    %esi, -8(%rbp)  # y
        movl    -4(%rbp), %eax  # x
        addl    $1, %eax        # x+1 
        movl    %eax, -12(%rbp) # x+1 -> temp 
        movl    -4(%rbp), %eax  # x
        subl    -8(%rbp), %eax  # x - y 
        movl    %eax, -16(%rbp) # x - y -> temp2  
        movl    -12(%rbp), %eax # temp
        imull   -16(%rbp), %eax # temp * temp2 -> return value 
        popq    %rbp            # 恢复 帧指针 
        retq
```

``` c

int foo(int x , int y){
  //char a = 0;
  int temp = x + 1;
  int temp2 = x - y ;
  return temp * temp2 ;
}

/* Type your code here, or load an example. */
int  __attribute__((noinline)) square() {
  char aa = 'a' ;
  long long le = 0;
  long long hi = 12;
  long long le1 = 0;
  long long hi1 = 12;
  long long le2 = 0;
  long long hi2 = 12;
  //foo(3,7); 使得 square()  是否为叶子过程 
  return le + hi;
}
struct foo { // > 16 字节, 在栈中要为其分配 32 字节. rsp -= 32  
  int i;
  long long l;
  long long ll;
};

int main() {
  struct foo myfoo;
  myfoo.i = 100;
  //square(); 使得 square()  是否为叶子过程 
  return 0;
}

// rsp 增长 按16字节对齐.

// 叶子过程可以不为其分配栈帧, 可直接使用 rbp - N 处的内存. 栈顶之外的128 字节都可以使用. 
```

``` asm
  foo:                                    # @foo
        pushq   %rbp
        movq    %rsp, %rbp
        movl    %edi, -4(%rbp)
        movl    %esi, -8(%rbp)
        movl    -4(%rbp), %eax
        addl    $1, %eax
        movl    %eax, -12(%rbp)
        movl    -4(%rbp), %eax
        subl    -8(%rbp), %eax
        movl    %eax, -16(%rbp)
        movl    -12(%rbp), %eax
        imull   -16(%rbp), %eax
        popq    %rbp
        retq
square:                                 # @square
        pushq   %rbp
        movq    %rsp, %rbp
        movb    $97, -1(%rbp)
        movq    $0, -16(%rbp)
        movq    $12, -24(%rbp)
        movq    $0, -32(%rbp)
        movq    $12, -40(%rbp)
        movq    $0, -48(%rbp)
        movq    $12, -56(%rbp)
        movq    -16(%rbp), %rax
        addq    -24(%rbp), %rax
        popq    %rbp
        retq
main:                                   # @main
        pushq   %rbp
        movq    %rsp, %rbp
        movl    $0, -4(%rbp)
        movl    $100, -32(%rbp)
        xorl    %eax, %eax
        popq    %rbp
        retq
```

### frame指针

frame指针的存在通常是为了变长的函数frame.
因为函数的返回需要退回栈顶指针sp,但是要退回到何处呢?
这就需要使用frame指针fp来标记一个frame的开始位置.

``` ocaml
let f x =
  g x
;;
```

例如 f 调用了 g. 调用前首先要保存f的fp, 然后将其fp修改为当前的sp.

当g返回时, 将sp置为当前的fp, 并取出保存的fp将其设置为当前fp.

       高
     ______
    | f的  |
    | 栈帧 |
    |______|
    | g的  |
    | 栈帧 |
    |______|

       低

当函数的栈帧大小固定时, 为了方便也仍然需要fp.
因为临时变量(中间结果)和保存的寄存器这些信息要到整个编译阶段的末尾才被计算出来.
这就意味着sp尚未确定, 因此不能只靠sp来索引入参/局部变量.
而入参/局部参数就在fp周围, 因此使用fp进行索引是很方便的.

### 保存寄存器

同一寄存器可能会被不同函数使用, 例如
f调用g,而它们都使用了1号寄存器来存放入参.

因此这个寄存器在调用的前或后需要被保存起来.防止f的参数被覆盖.

到底是调用者还是被调者进行保存是根据约定来的, 寄存器被分成两类,
`caller-save` , `callee-save` .
冲突的寄存器由谁进行保存要查阅寄存器的约定使用方式.

因为保存&恢复寄存器涉及到两次内存的访问, 因此要避免不必要的寄存器保存.
若冲突的寄存器在被调用函数返回后不再被使用,那么就没有必要保存它.

寄存器分配将负责决定局部变量&临时变量该位于哪种保存类型的寄存器.

### 优化参数传递

就像上节中举的例子, f(x)调用g(x)会发生寄存器的冲突,
因此最简单的方案是保存&恢复冲突的寄存器.

但是这种方案会增加内存的存取次数, 对性能不利.
有没有方案可以避开寄存器冲突呢?

- 内联叶子过程:

  不为叶子过程分配栈帧, 自然也就没有入参冲突.

- 识别dead参数

  不去保存那些在被调函数返回后无用的参数

- 过程间寄存器分配:

  全局分析所有函数, 用不同的寄存器来避开冲突的入参传递.

- 机器体系结构支持多组寄存器

入参一部分存放在寄存器中, 另一部分存放在栈中. 对寄存器参数来说,
需要很多额外的处理:

如何获取入参的地址?

对于后者,取地址是容易. 如何取寄存器参数中的地址呢?
可以识别这些被取了地址的变量, 然后将其紧挨着栈中参数存放.
亦或是为所有寄存器参数都保留栈中的空间.但不写入内容.

### 返回地址

返回地址由call保存到指定寄存器中,

对于非叶子过程, 因为它仍要调用其他函数, 会覆盖掉寄存器中的返回地址,
因此它需要额外将返回地址存入stack中.
对于叶子节点,则无需额外将返回地址stack中,
因为寄存器中的返回地址不会被覆盖.

### 驻留frame中的变量

对于局部变量和中间结果, 应该优先将他们存入寄存器.
只有迫不得已时才存入栈中.

- 该变量被取过地址.
- 该变量是一个数组, 本质上也要取其地址.
- 该变量的值过大, 无法存入寄存器.
- 溢出: 局部变量&临时变量太多, 无法全都存入寄存器
- 此变量被嵌套定义的内层函数使用.
- 此变量要让出占用的寄存器时, 可能会被临时保存到stack中.

为这种变量取个名字:

**逃逸变量**: 该变量为传地址实参/ 被取了地址 / 被内层函数访问.

逃逸变量必须分配在stack中!(逃脱了寄存器)
在首次遇到变量声明时无法确定是否是逃逸变量.
因此很多编译器先将所有变量分配到栈中, 之后的pass再决定是否能放入寄存器.

### 静态链

静态链主要是为了支持嵌套的函数定义.
内层函数有可能会直接使用外层函数中的局部变量.
因此需要一个方法能在内层函数中访问外层函数的栈帧.

可以为每个函数传入一个额外的参数, 此参数指向外层定义的函数(栈帧)

``` ocaml
let myfunc x = 
   let
     bar y = x + y 
   in 
   (bar 100)
;;
```

调用 bar 时要额外传入一个参数, 它指向myfunc的栈帧.

## frame概览

高阶函数 -\> 嵌套定义的函数 -\> 逃逸变量(内存中) -\> 静态链访问

``` ocaml
    Semant 
  TRANSLATE    接口 
  Translate    实现
FRAME    TEMP  接口
Frame    Temp  实现
```

在语义分析阶段之前, 先对AST调用 `FindEscape` 将是否为逃逸变量标记好.

函数声明:

`Semant.transDec` -\> `Translate.newlevel` -\> `Frame.newFrame`

`Frame` 层不知道静态链的存在, 而上层的 `Translate` 负责静态链的分配.

局部变量声明:

`Frame.access` 代表了变量存放的位置: 内存/寄存器?

`Translate.access` 比它多了level信息

`Semant + lev` -\> `Translate.allocLocal lev esc` -\> `Frame.allocLocal`
==\> 返回 access

## 实现思路

函数中可以有局部变量. 每次函数调用都会创建一份其局部变量的实例.

Tiger编译器的栈帧

栈帧的接口:

``` ocaml
module type FRAME = sig
  type frame
  type access

  val newFrame: {name:Temp.label,formals:bool list} -> frame
  val allocLocal: frame -> bool -> access

  val name: frame -> Temp.label
  val formals: frame -> access list
  ...
end
```

``` ocaml
module type FRAME =  sig
  type register = string
  val RV: Temp.temp (*p. 168*)
  val FP: Temp.temp (*p. 155*)
  val registers: register list
  val tempMap: register Temp.Table.table
  val wordSize: int (*p. 155*)
  val externalCall: string * Tree.exp list -> Tree.exp (*p. 165*)

  type frame (*p. 134*)
  val newFrame: {name: Temp, label, formals: int} -> frame * int list  (*p. 135*)
  val formals: frame -> access list (*p. 135*)
  val name: frame -> Temp.label (*p. 134*)
  val allocLocal: frame -> int (*p. 137*)
  val string: Tree.label * string -> string (*p. 262*)
  (* (L3,"hello") ==> "L3: .ascii "hello" \n" *)
  val procEntryExitl: frame * Tree.stm -> Tree.stm (*p. 261*)
  val procEntryExit2: frame * Assem.instr list -> Assem.instr list  (*p. 208*)
  val procEntryExit3 : frame * Assem.instr list -> (*p. 261*)
{prolog: string, body: Assem.instr list, epilog: string}

  type frag = PROC of { body: Tree.stm, frame: frame}  (*p. 169*)
    | STRING of Temp.label * string
end
```

特定的目标机器:

``` ocaml
module MipsFrame : FRAME = struct
  ...
end
```

实现:

``` ocaml
module Frame : FRAME = MipsFrame ;; 
```

创建一个新的栈帧对象:

``` ocaml
Frame.newFrame { name=g; formals= [true;false;false] };;
```

``` ocaml
module MipsFrame: FRAME = struct
  ...
  type access = InFrame of int
      | InReg of Temp.temp 
  ...
end
```

``` ocaml
Frame.allocLocal f true ;;
(* 返回一个 Frame.access of InFrame 类型的值 *)
```

``` ocaml
module FIND_ESCAPE = sig
  val findEscape: Absyn.exp -> unit
end

module FindEscape : FIND_ESCAPE = struct
  type depth = int
  type escEnv = (depth * bool ref) Symbol.table (* symbol --> (嵌套层级深度, 是否为逃逸变量) *)

  let traverseVar (env:escEnv) (d:depth) (s:Absyn.var) : unit = (* ... *) ;;
  and traverseExp (env:exvEnv) (d:depth) (s:Absyn.exp) : unit = (* ... *) ;;
  and traverseDecs (env:exvEnv) (d:depth) (s:Absyn.dec list) : escEnv =  (* ... *) ;;

  let findEscape (prog: Absyn.exp) : unit = (* ... *) ;;
end
```

当在静态函数嵌套深度为 `d` 处发现了一个 **变量声明** / **形参声明**,
例如:

``` ocaml
VarDec {name=symbol("a"); escape=r; (* ... *)} 
```

则将类型为 `bool ref` 的值设为 `false`. 将绑定 `"a" -> (d,r)`
加入到环境(`escEnv`)中.

这个新环境被用在和这个变量处于同一作用域中的表达式中. 每当发现了符号 `a`
在深度大于 `d` 的地方被使用, 就将其绑定中的 `r` 设为 `true`.

`temp` 是局部变量的抽象名字. `label` 是静态内存地址的抽象名字.

模块 `Temp` 管理着两个不同名字的集合.

``` ocaml
module type Temp = sig

  type temp
  module Table = Map.Make(temp)  (* 其中Table的key是temp类型的 *)
  val newtemp : unit -> temp
  val makestring : temp -> string

  type label = Symbol.symbol
  val newlabel: unit -> label
  val nemedlabel : string -> label

end
```

``` ocaml
module type TRANSLATE = sig 
  type level  
  type access (** 和Frame.access不同,多了level这一信息. *)
  val outermost : level

  val newLevel: {parent: level; name:Temp.label; formals: bool list} -> level
  val allocLocal: level -> bool -> access
end


module Translate : TRANSLATE = struct
  ...
  type access = level * Frame.access  (* <<=!! *)
  ...
end
  ;;
```

语义分析阶段中的 `transDec` 通过调用 `Translate.newLevel`
为每个函数声明创建一个新的嵌套层级. 这个函数又调用 `Frame.newFrame`
创建了一个新的栈帧. `Semant` 将 `level` 保存在此函数的 `FunEntry`
数据结构中, 使得每遇到一个函数调用时, 可以将被调用函数( `FunEntry` )的
`level` 字段传回 `Translate` 模块. `FunEntry`
也需要函数的机器代码的入口处作为 `label` 字段.

``` ocaml
module type Env = sig
  (** 新版本的VarEntry和FunEntry : *)
  type enventry =
  VarEntry of { access:Translate.access; ty:ty }
    | FunEntry of {
    level: Translate.level;
    label: Temp.label;
    formals: ty list;
    result: ty
  }

  ...
end
```

当 `Semant` 处理一个位于层级为 `lev` 的局部变量时, 它会调用
`Translate.allocLocal lev esc` 在本层级中创建一个变量. 参数 `esc`
表示是否是逃逸变量. 其返回结果为 `Translate.access`,
这是一个抽象数据类型(但不同于 `Frame.access`,
因为它必须包含关于静态链的信息). 之后, 当变量在一个表达式中被使用时,
`Semant` 可以将其 `access` 传回 `Translate` ,
以便于生成访问此变量的机器代码. 与此同时, Semant在值环境中记录着每个
`VarEntry` 中 `access` .

抽象数据类型 `Translate.access` 可以被实现为变量的level和其
`Frame.access` 的偶对:

``` ocaml
type access = level * Frame.access
```

使得 `Translate.allocLocal` 能调用 `Frame.allocLocal`,
并且还可以记住变量是位于哪个层级的. 层级信息稍后在计算静态链时要用到,
变量可能从一个不同的层级中被访问.

`Frame`
应该独立于被编译的特定语言.许多语言没有嵌套的函数声明.因此Frame不应包含关于静态链的信息,
这是 `Translate` 的责任. `Translate` 知道每个栈帧包含着一个静态链.
静态链用寄存器被传给一个函数,
并将其存储到栈帧中.因为静态链表现得如此接近于一个形式参数,
我们将它看成是一个形参. 对于一个有着k个正常参数的函数,令 `l`
是标识其参数是否为逃逸变量的bool列表.则: `l' = true::l` 是一个新的list.
额外的true标识着静态链这个额外参数是逃逸的. 于是 `newFrame(label,l')`
创建了一个包含额外参数和其形参的栈帧.

例: 函数 `f(x,y)` 被嵌套在函数 `g` 中.并且g的level被记为 `lev_g`. 于是
`Semant.transDec` 可以调用:

``` ocaml
Translate.newLevel {parent=lev_g;name=f;formals= [false;false] }
```

并假设 `x,y` 都不是逃逸变量.于是 `Translate.newLevel` 为形参的 `bool`
列表又加了一个元素:

``` ocaml
Frame.newFrame { label, [true;false;false] } 
```

它会返回一个 `frame` . 在这个 `frame` 中,有三个栈帧偏移类型的值,
可以通过 `Frame.formals(frame)` 来访问.
返回值的首个元素是静态链在栈帧中的偏移量, 其它两个是参数 `x, y`
的偏移量.当 `Semant` 调用 `Translate.formals(level)` 时 ,
它会得到这两个偏移量,并将其转换为 `access` 类型的值.

对层级保持追踪

每次对 `Translate.newLevel` 进行调用, `Semant` 必须传递外面这层的
`level` 值. 当为Tiger程序的main创建level时, Semant应当传递一个特殊的
`level` 值: `Transale.outermost` . 它不是Tiger的main函数的level,
而是包含了main的过程的level.所有库函数位于这个 `outermost` 层级.

函数 transDec 会为每个函数声明创建一个新的level,
但必须将外围函数的level传给newLevel. 这意味着 transDec
中必须包含了当前level的信息.

实现这点是很容易的, 为transDec增加额外的参数, 代表了当前的level.
并且也为transExp增加一个level参数,
这样当遇到一个函数声明时便可将level传递给 transDec.

transVar 也需要添加一个表示当前level的参数,
因为要通过计算level的差来决定访问几次静态链.

# 中间表示

``` ocaml
module type TREE = sig
  type exp = Const of int       (* 整数常量 *)
       | Name of Temp.label (* 符号常量,对应于汇编中的标签 *)
       | Temp of Temp.temp  (* 在抽象机器中的临时量,类似于真正机器中的寄存器 *)
       | Binop of binop * exp * exp (* 二元运算 *)
       | Mem of exp    (*在地址处长度为Frame.wordSize的内容,在左侧和右侧的用法不同*)
       | Call of exp * exp list (*过程调用*)
       | Eseq of stm * exp (*stm用于副作用,exp作为结果*)

  and stm = Move of exp * exp 
      | Exp of exp
      | Jump of exp * Temp.label list (* 类似于 switch *)
      | Cjump of relop * exp * exp * Temp.label * Temp.label (* 类似于if-else *)
      | Seq of stm * stm
      | Label of Temp.label

  and binop = Plus | Minus | Mul | Div | And | Or | Xor | Lshift | Rshift | Arshift

  and relop = Eq | Ne | Lt | Gt | Le | Ge | Ult | Ule | Ugt | Uge
end
```

语句stm主要负责副作用和控制流

- `Move(Temp t, e)` : 对e进行求值, 并将它移动到t中.
- `Move(Mem(e1),e2)` : 对e1求值,得到地址a. 然后对e2进行求值,
  将结果存储到以a为开始长度为wordSize的内存中.
- `Exp(e)` 对e求值,并忽略结果.
- `Jump(e,labs)` 将控制流转移至地址e处. 目标e必须是形式为 `Name(lab)`
  的文本标签,或是可以被计算为一个地址的表达式. 例如 类C语言中的
  `switch(i)` 语句可能通过在 `i` 上做算术来实现. 标签列表 `labs`
  指定了所有e的可能的求值结果; 这对于之后的数据流分析是必要的.
  跳往一个已知的标签可以用 `Jump(Name l, [l])` .
- `Cjump(o,e1,e2,t,f)` 对e1,e2分别求值, 得到值 a, b. 然后使用关系运算符
  `o` 对a,b进行比较. 若结果为true, 则跳到t; 否则跳到f. 使用 Eq, Ne
  测试整数的相等性和不等性.
  用Lt,Gt,Le,Ge比较有符号整数的大小关系.用Ult,Ugt,Ule,Uge比较无符号整数的大小关系.
- `Seq(s1,s2)` 语句s1 s2组成的序列
- `Label(n)` 定义一个名字常值n为当前机器码的地址. 这类似于汇编中的标签.
  `Name(n)` 的值可以作为jump,call等的目标.

翻译为树

将抽象语法转换为中间表示树是十分直接的, 但仍有许多要处理的情况.

表达式的种类:

返回一个值的表达式. 不返回(有意义)值的表示式(while/返回值为空的过程调用)
bool表达式:

抽象语法树中的exp类型用Tree语言该如何表示呢? 乍一看似乎要用
Tree.exp进行表示. 然而这只对某些种类的表达式是可行的,
即能被计算为一个值的那些表达式.
而对于那些不返回值的表达式(例如某些过程调用或是while表达式)
用Tree.stm来表示它们是更加自然的. 并且对于那些有bool类型值的表达式,
例如a\>b, 可能最好的表示方式是作为一个有条件跳转:
Tree.stm和用Temp.label表示的目的地的组合成的pair.

因此,我们在 `Translate` 增加 `exp` 类型, 分别表示这三类表达式:

``` ocaml
type exp = Ex of Tree.exp
     | Nx of Tree.stm
     | Cx of (Temp.label * Temp.label -> Tree.stm)
```

- `Ex` : 代表一个有值的表达式, 用Tree.exp进行表示.
- `Nx` : 代表无值的表达式, 表示为 Tree.stm
- `Cx` : 代表有条件跳转, 被表示为一个函数, 将一对标签映射为一个语句.
  若给这个函数传入一个true目的地和一个false目的地, 则它会创建一个语句,
  此语句会对某个条件进行求值, 并据此跳转到其中的一个目的地.
  (此表达式绝不会因为不满足条件而直接向下执行.)

例如 Tiger表达式 `a>b | c<d` 可能被翻译为:

``` ocaml
Cx (
  fun (t,f) -> Seq (Cjump Gt a b t z, Seq (Label z, Cjump Lt c d t f) )
)
```

``` rust
 if a>b  {     --+
     goto t;     |
 } else {        |--> Cjump Gt a b t z
     goto z;     |
 }             --+

 label z :     |--->  Label z 

 if c<d {      --+
     goto t;     |
 } else {        |--> Cjump Lt c d t f
     goto f;     |
 }             --+


//??  label t:

//??  label f: 
```

``` ocaml
unEx : exp -> Tree.exp

unNx : exp -> Tree.stm

unCx : exp -> (Temp.Label -> Temp.Label -> Tree.stm) 
```

这三种逆转构造函数中的每个能作用在Translate.exp的三种类型上,
就像下面实现的unEx.

``` ocaml
module T = Tree

let unEx ex = match ex with
  | Ex e -> e 
  | Cx genstm -> 
    let r = Temp.newtemp () in
    let t = Temp.newlabel () in
    let f = Temp.newlabel () in
    begin 
  T.Eseq (
    T.Seq(T.Move (T.Temp r,T.Const 1) ,
      T.Seq (genstm t f,
             T.Seq(T.label f,
               T.Seq(T.Move(T.Temp r,T.Const 0) ,
                 T.Label t
                )))) ,
    T.Temp r)
    end
  | Nx s -> T.Eseq s (T.Const 0)
```

`unEx` 为bool表达式生成的 `Tree.exp` 类似于:

``` rust
  r <- 1
  genstm t f  // 何时跳转到t和f的语句
label f :
  r <- 0
label t :
  r
```

``` ocaml
  module type FRAME =  sig

    type register = string

    val RV: Temp.temp (*p.168*)
    val FP: Temp.temp (*p.155*)
    val registers: register list
    val tempMap: register Temp.Table.table
    val wordSize: int (*p.155*)
    val externalCall: string * Tree.exp list -> Tree.exp (*p.165*)

    type frame (*p.134*)
(** val newFrame: {name: Temp.label, formals: int} -> frame * int list  (*p.135*)  *)
    val newFrame: {name: Temp.label, formals: bool list} -> frame
    val formals: frame -> access list (*p.135*)
    val name: frame -> Temp.label (*p.134*)
(** val allocLocal: frame -> int (*p.137*) *)
    val allocLocal: frame -> bool -> access
    val string: Tree.label * string -> string (*p.262*)
    (* (L3,"hello") ==> "L3: .ascii "hello" \n" *)

    val procEntryExitl: frame * Tree.stm -> Tree.stm (*p.261*)
    val procEntryExit2: frame * Assem.instr list -> Assem.instr list  (*p.208*)
    val procEntryExit3: frame * Assem.instr list -> {prolog: string, body: Assem.instr list, epilog: string} (*p.261*)

    type frag = PROC of { body: Tree.stm, frame: frame}  (*p.169*)
      | STRING of Temp.label * string

  end
```

``` ocaml
module type TRANSLATE = sig
  (* ... *)
  val procEntryExit  : {level: level, body: exp} -> unit
  module Frame: FRAME
  val getResult  : unit -> Frame.frag list
end
```
