# Ch5

## complex synonym

``` ocaml
module type ComplexSig = sig
  val zero : float * float
  val add : float * float -> float * float -> float * float
end
```

这是一个表示复数的module type 为它添加 `type t = float * float`
对代码进行改进.

``` ocaml
module type ComplexSig = sig
  type t = float * float
  val zero : t
  val add : t -> t -> t
end
```

## complex encapsulation

``` ocaml
module Complex : ComplexSig = struct
  type t = float * float
  let zero = (0., 0.)
  let add (r1, i1) (r2, i2) = r1 +. r2, i1 +. i2
end
```

分别进行如下的修改, 并观察出现的错误:

- 移除 `zero`

<!-- -->

    Error: Signature mismatch:
           Modules do not match:
             sig
               type t = float * float
               val add : float * float -> float * float -> float * float
             end
           is not included in
             ComplexSig
           The value `zero' is required but not provided

- 移除 `add`

``` ocaml
Error: Signature mismatch:
       Modules do not match:
         sig type t = float * float val zero : float * float end
       is not included in
         ComplexSig
       The value `add' is required but not provided 
```

- 修改 `zero` 为 `let zero = 0, 0`

``` ocaml
Error: Signature mismatch:
       ...
       Values do not match:
         val zero : int * int
       is not included in
         val zero : t
```

## big list queue

使用下列代码创建长度成倍增长的 ListQueue : 10, 100, 1000 …
在出现明显的延迟之前最大能创建多长的 Queue ?
在出现10s以上的延迟之前能创建的最长的Queue ?

``` ocaml
  module type Queue = sig
    type 'a t
    exception EmptyQueue
    val empty : 'a t
    val is_empty : 'a t -> bool
    val size : 'a t -> int
    val enqueue : 'a -> 'a t -> 'a t
    val front : 'a t -> 'a
    val dequeue : 'a t -> 'a t
    val to_list : 'a t -> 'a list 
  end

module ListQueue : Queue = struct
  type 'a t = 'a list
  exception EmptyQueue
  let empty = []
  let is_empty = function
    | [] -> true
    | _ -> false
  let size = List.length

  let enqueue e q = q @ [e]  (* !! *)
  let front = function
    | [] -> raise EmptyQueue
    | h::_ -> h
  let dequeue = function
    | [] -> raise EmptyQueue
    | _::t -> t 
  let to_list = Fun.id (* 恒等映射 *)
end
```

``` ocaml
(** Creates a ListQueue filled with [n] elements. *)
let fill_listqueue n =
  let rec loop n q =
    if n = 0 then q
    else loop (n - 1) (ListQueue.enqueue n q) in
  loop n ListQueue.empty
;;
```

A1: fill<sub>listqueue</sub> 10000 ;;

A2: fill<sub>listqueue</sub> 100000 ;;

## big batched queue

用下面的代码来重复上题的实验

``` ocaml
module  BatchedQueue = struct

  type 'a queue = {
    front: 'a list ;
    back: 'a list 
  }

  let empty = {
    front= [];
    back = []
  }

  let peek = function
    |{front=[] } -> None
    |{front=x::_ ;} -> Some x


  let enqueue x = function
    |{front=[] } -> {front=[x] ; back=[] }
    |q -> {q with back=x::q.back}  (* 即：当front不为空list时*)

  let dequeue = function
    |{front=[]} -> None
    |{front= _::[] ;back=b} -> Some {front = List.rev b ;back=[] } 
    |{front=_::t;back=b} -> Some {front = t ;back=b}

end
```

``` ocaml
let fill_batchedqueue n =
  let rec loop n q =
    if n = 0 then q
    else loop (n - 1) (BatchedQueue.enqueue n q) in
  loop n BatchedQueue.empty
```

此时才会出现10s以上的延迟 fill<sub>batchedqueue</sub> 1000000000 ;;

## queue efficiency

比较两种入队 `enqueue` 操作的实现.用你自己的话解释为何
`ListQueue.enqueue` 是线性时间的.

考虑 `BatchedQueue.enqueue` 假设

## binary search tree map

编写module `BstMap` , 用二叉搜索树实现 `Map` 模块, 每个节点应该存储一个
pair (key,value)

``` ocaml
module type Map = sig
  exception Empty
  type ('k,'v ) t
  val empty : ('k,'v) t
  val insert : 'k -> 'v -> ('k,'v) t -> ('k,'v) t
  val lookup : 'k -> ('k,'v) t -> 'v 
  val bindings : ('k,'v) t -> ('k * 'v) list  
end ;;


module BstMapImpl = struct
  exception Empty
  type ('k,'v) t = Leaf | Node of ('k * 'v) * ('k,'v) t * ('k,'v) t 
  let empty = Leaf
  let rec  insert key value = function
    | Leaf -> Node ( (key,value) ,Leaf,Leaf)
    | Node ((k,v),l,r) when key < k ->  Node((k,v),(insert key value l),r) 
    | Node ((k,v),l,r) when key > k ->   Node((k,v),l,(insert key value r))
    | Node ((k,v),l,r) -> Node((k,value),l,r)

  let rec lookup key = function
    | Leaf -> raise  Empty
    | Node ((k,_),l,_) when key < k ->  lookup key l
    | Node ((k,_),_,r) when key > k -> lookup key r
    | Node ((_,v),_,_) -> v

  let bindings m  =
    let rec bindings_aux acc  = function
    | Leaf -> acc 
    | Node((k,v),l,r) ->  (bindings_aux (bindings_aux ((k,v)::acc)  l) r)
    in
    bindings_aux [] m 
end

module BstMap:Map = BstMapImpl ;;
```

``` ocaml
# BstMapImpl. (empty |> insert 1 "hello" |> insert 2 "fuck" |> insert 4 "dead" |> lookup 2 ) ;;
- : string = "fuck"

# BstMapImpl. (empty |> insert 1 "hello" |> insert 2 "fuck" |> insert 4 "dead" |> bindings  ) ;; 
- : (int * string) list = [(4, "dead"); (2, "fuck"); (1, "hello")]
```

## fraction

实现下面的分数 `Fraction` 模块type

``` ocaml
module type Fraction = sig
  (* A fraction is a rational number p/q, where q != 0.*)
  type t

  (** [make n d] is n/d. Requires d != 0. *)
  val make : int -> int -> t

  val numerator : t -> int
  val denominator : t -> int
  val to_string : t -> string
  val to_float : t -> float

  val add : t -> t -> t
  val mul : t -> t -> t
end


module TupleFraction : Fraction = struct
  type t = int * int

  let make n d =if d=0 then raise Division_by_zero else  (n ,d )
  let numerator (n,d) = n
  let denominator (n,d) = d
  let to_string (n,d) = ( string_of_int n ) ^ "/" ^ (string_of_int d)
  let to_float (n,d) = (float_of_int n) /. (float_of_int d)

  let add (n,d) (n',d') =  (n*d' + n' *d , d*d' )
  let mul (n,d) (n',d') = (n*n'  ,d*d') 
end
```

## fraction reduced

实现自动约分到最简形式的分数 分母要保持为正数

``` ocaml
(** [gcd x y] is the greatest common divisor of [x] and [y].
    Requires: [x] and [y] are positive. *)
let rec gcd x y =
  if x = 0 then y
  else if (x < y) then gcd (y - x) x
  else gcd y (x - y)
```

``` ocaml


module ReducedFraction : Fraction = struct
    type t = int * int

    let rec mygcd x y = 
  if x mod y = 0 then y 
  else if x < y then mygcd y x 
  else  mygcd y (x mod y)

    let reduce (n,d) = let g = mygcd n d in (n/g, d/g ) 
    let make n d =if d=0 then raise Division_by_zero else reduce (n,d)


    let numerator (n,d) = n
    let denominator (n,d) = d
    let to_string (n,d) = ( string_of_int n ) ^ "/" ^ (string_of_int d)
    let to_float (n,d) = (float_of_int n) /. (float_of_int d)

    let add (n,d) (n',d') =  reduce (n*d' + n' *d , d*d' )
    let mul (n,d) (n',d') = reduce (n*n'  ,d*d') 
  end
```

## make char map

为了创建标准库中的map, 我们要使用functor `Map.Make`
创建一个特化了key的module:

``` ocaml
module CharMap = Map.Make(Char) ;; 
```

这产生了一个signature

``` ocaml
module CharMap :
  sig
type key = Char.t
type 'a t = 'a Map.Make(Char).t
   ...
val empty : 'a t
val add : key -> 'a -> 'a t -> 'a t
val remove : key -> 'a t -> 'a t
    ...
end
```

## char ordered

functor `Map.Make` 需要一个和 `Map.OrderType` 相匹配的module. 查看
`Char` 和此module的文档, 解释为何 `Char` 能作为 `Map.Make` 的参数. 因为
OrderType 中有两个声明 :

    type t : key的类型
    val compare : t -> t -> int  用来比较key的函数 (k1 - k2)

而 `Char` 中也有这两个定义:

``` ocaml
type t = char 
(**  An alias for the type of characters. *)

val compare : t -> t -> int
(**  The comparison function for characters, with the same specification as compare. Along with the type t, this function compare allows the module Char to be passed as argument to the functors Set.Make and Map.Make. *)
```

因此 Char 满足 signature `Map.Ordertype`

## use char map

使用 `CharMap` 创建包含下述内容

- 'A' maps to "Alpha"

- 'E' maps to "Echo"

- 'S' maps to "Sierra"

- 'V' maps to "Victor"

用 `CharMap.find` 寻找'E'的值. 移除 'A'的绑定. 使用 `CharMap.mem`
检查是否 'A' 仍存在绑定. 使用 `CharMap.bindings` 将 map 转化为
accociation list.

``` ocaml
let m = CharMap. (empty |> add 'A' "Alpha" |> add 'E' "echo" |> add 'S' "Sierra" |> add 'V' "Victor" ) ;;

CharMap.find 'E' m ;;
(** - : string = "echo" *)
m |>  CharMap.remove 'A' |>  CharMap.mem 'A';;
(** - : bool = false *)
CharMap.bindings m ;;
(** [(A, "Alpha"); (E, "echo"); (S, "Sierra"); (V, "Victor")] *)
```

## bindings

查看 `Map.S` 的文档, 找到 bindings 的规范, 下面哪几个表达式会返回相同的
alist?

- `CharMap.(empty |> add 'x' 0 |> add 'y' 1 |> bindings)`

- `CharMap.(empty |> add 'y' 1 |> add 'x' 0 |> bindings)`

- `CharMap.(empty |> add 'x' 2 |> add 'y' 1 |> remove 'x' |> add 'x' 0 |> bindings)`

三个表达式返回的 alist 都是相同的. 因为根据规范,
返回的list是按照key的顺序排序的, 因此和添加的顺序无关.

    val bindings : 'a t -> (key * 'a) list

    Return the list of all bindings of the given map. The returned list is sorted in increasing order of keys with respect to the ordering Ord.compare, where Ord is the argument given to Stdlib.Map.Make

## date order

``` ocaml
type date = {month : int; day : int}
```

例如 3月31日被表示为 `{month = 3; day = 31}` .
下面将会实现一个key的类型为date的Map. 显然这可能会存在无效的日期: {month
= 2 ; day = 89} 对无效日期的行为不做特殊规定. 为了用 `Map.Make` 生成Map,
我们需要实现 Map.OrderedType signature.

``` ocaml
module Date = struct
  type date = {month :int ; day : int} 
  type t = date
  let compare d1 d2 = match (d1.month - d2.month  , d1.day-d2.day) with
    | (m,d) when m > 0 -> 1
    | (m,d) when m < 0 -> -1
    | (0,d) when d > 0 -> 1
    | (0,d) when d < 0 -> -1
    | _ -> 0
end
```

## calender

用上一问的 `Date` 和 `Map.Make` 创建 `DateMap` module, 并定义一个 日历
`calendar` 类型:

``` ocaml
type calendar = string DateMap.t ;;
```

其想法是将日期映射到那天要进行的事件名称. 使用 `calender` 加入几个日期:

``` ocaml
DateMap. (empty |> add {month=10;day=12} "my birthday!" |> bindings) ;; 
```

## print calendar

编写函数 `print_calendar: calendar -> unit` 它打印日历中所有元素

``` ocaml
let print_calendar (cal:calender) =
  DateMap.iter (fun d e -> Printf.printf "%i月%i日: %s \n" d.month d.day e ) cal 
```

## is for

编写函数 `is_for: string CharMap.t -> string CharMap.t` 使得将一个绑定为
`ki -> vi` 的Map,映射为绑定为 `ki -> "ki is for vi"` . 提示:
用Map.S中的函数可以得到一个只有一行的解答. 为了将字符转换为string,
可以用 `String.make` , 更高级的做法是用 `Printf.sprintf`

``` ocaml
let is_for m =
  CharMap.mapi (fun k v -> Printf.sprintf "%c is for %s" k v ) m
;;
```

``` ocaml
# CharMap. (empty |> add 'a' "apple" |> is_for |> bindings) ;;
- : (CharMap.key * string) list = [(a, "a is for apple")]
```

## first after

编写函数 `first_after : calendar -> Date.t -> string` ,
它返回在给定日期之后(不包含该日期)的首个事项的名称. 若没有这样的事件,
函数应抛出 `Not_found` 异常.(它是标准库中定义的异常) 提示: 可用 `Map.S`
中的函数来完成仅有一行的解答.

``` ocaml
let first_after (cal:calendar) (d:Date.t) =
 let (d,e) = DateMap.find_first (fun k -> (Date.compare k d) > 0) cal
 in e
;;
```

``` ocaml
#  first_after (DateMap. (empty |> add {month=10;day=12} "my birthday!" )) {month=10;day=1} ;; 
- : string = "my birthday!"

#  first_after (DateMap. (empty |> add {month=10;day=12} "my birthday!" )) {month=11;day=1} ;; 
Exception: Not_found
```

## sets

标准库中的 `Set` 模块十分类似于 `Map` ,
使用它创建一个代表了大小写不敏感字符串的集合.
仅仅是大小写不同的两个字符串集合应视作相同.

``` ocaml
module InsStr= struct 
  type t = string
  let compare a b =String. (compare (lowercase_ascii a) (lowercase_ascii b))
end


module InsStrSet = Set.Make(InsStr );; 
```

## tostring

编写module type `ToString` 指定一个signature, 它包含了抽象类型t,
和一个函数 `to_string : t -> string`

``` ocaml
module type ToString = sig
  type t
  val to_string : t -> string
end
```

## Print

编写functor `Print` ,它接收一个名为 `M` 的 `ToString` 模块,
并返回一个只有一个 `print: M.t -> unit` 定义的模块,
此函数打印出值的字符串表示.

``` ocaml
module Print (M:ToString) = struct
  let print (m:M.t) =
    Printf.printf "%s\n" (M.to_string m)
end
```

## Print Int

创建模块 `PrintInt` 作为应用functor `Print` 到 `Int` 上的结果. 编写
`Int` 模块, 其 `Int.t` 应为 int.

``` ocaml
module Int = struct
  type t = int
  let to_string = string_of_int
end

module PrintInt = Print(Int) ;; 
```

``` ocaml
# PrintInt.print 234 ;;
234
- : unit = ()
```

## Print String

创建名为 `PrintString` 的模块, 它是应用 `Print` 到 `MyString` 上的结果.

``` ocaml
module MyString = struct
  type t = string
  let to_string = Fun.id
end

module PrintString = Print(MyString) ;; 
```

``` ocaml
# PrintString.print "hello"  ;;
hello
- : unit = ()
```

## Print Reuse

解释 `Print` 是如何实现代码复用的?

打印值这一函数需要值的类型, 和如何将此类型的值转化为字符串.
除此之外的逻辑都是相同的. 因此将这两个不同点打包成一个module type:
`ToString` ,并针对输入为 `ToString` 这样的模块产生相应的打印函数.

## Print String reuse revisited

`PrintString` 模块仅支持一个操作: `to_string` ,
现在希望不用copy的方式创建一个包含了 `String` 模块中所有函数并且含有
`print`. 定义模块 `StringWithPrint` 提示: 使用两个include语句

``` ocaml
module StringWithPrint = struct
  include String
  include Print(MyString) 
end
```

## implementation without interface

创建 `date.ml` 并包含下面的代码:

``` ocaml
type date = {month : int; day : int}
let make_date month day = {month; day}
let get_month d = d.month
let get_day d = d.day
let to_string d = (string_of_int d.month) ^ "/" ^ (string_of_int d.day)
```

创建 `dune` 文件

``` elisp
(library
 (name date)) 
```

加载此库文件到utop:

``` ocaml
dune utop 
```

在utop中, open `Date`, 创建一个日期,并访问它的day字段,
并将日期转换为string

``` ocaml
# open Date ;;

# (make_date 3 5 ) |> get_day ;;
- : int = 5

# (make_date 3 5 ) |> to_string ;;
- : string = "3/5"
```

## implementation with interface

继续上一个问题, 创建文件 `date.mli`

``` ocaml
type date = {month : int; day : int}
val make_date : int -> int -> date
val get_month : date -> int
val get_day : date -> int
val to_string : date -> string
```

并在utop中重复上一问中的操作

``` ocaml
# open Date ;;

# (make_date 3 6) |> get_day ;;
- : int = 6

# (make_date 3 6) |> to_string ;;
- : string = "3/6"

# let d = make_date 3 6 ;;
val d : date = {month = 3; day = 6}
```

## implementation with abstracted interface

在上两个问题的基础上, 修改 `date.mli` 中的第一行 为:

``` ocaml
type date 
```

现在类型date变为抽象的. 重复之前的操作.观察不同之处.

``` ocaml
# open Date;;

# let d = make_date 3 6 ;;
val d : date = <abstr>

# d |> get_day ;;
- : int = 6

# d |> to_string ;;
- : string = "3/6"

```

## printer for date

为 `date.mli` 添加声明

``` ocaml
val format : Format.formatter -> date -> unit 
```

并且添加一个 `format` 的定义到 `date.ml` 提示: 使用 `Format.fprintf` 和
`Date.to_string`

重新编译,并加载到utop, load "date.cmo" ,并安装 date的格式化器

``` ocaml
#install_printer Date.format;;
```

**解答:**

``` ocaml
let format f d =
  Format.fprintf f "%s" (to_string d)
```

    ocamlc date.mli
    ocamlc date.ml 

``` ocaml
utop # #load "date.cmo" ;;

utop # #install_printer  Date.format ;;

utop # open Date ;;

utop # let d = make_date 3 4 ;;
val d : date = 3/4

utop # d |> get_day ;;
- : int = 4

utop # d |> to_string ;;
- : string = "3/4"
```

## refactor arith(算术)

下载文件 [ `algebra.ml` ](./algebra.ml)
,它包含了两个signatures和四个structures

1.  环是描述称为环的代数结构的签名，环是加法和乘法运算符的抽象。

2.  域是描述代数结构的签名，称为域，它就像一个环，但也有一个除法运算的抽象。

3.  IntRing 和 FloatRing 是根据 int 和 float 实现环的结构。

4.  IntField 和 FloatField 是根据 int 和 float 实现字段的结构。

5.  IntRational 和 FloatRational
    是根据比例（也称为分数）实现字段的结构，即 int pair 和 float pair

使用 `include`, functor,
引入额外的structure/signature来提高代码复用的数量. 这有一些关于重构建议:

- 不要在一个以上的sig中 **直接声明** name,
  而是要用include的方式引入已有的名字 .

- 只需要分别为 `int`, `float` , 分数 **直接定义** 三次代数操作和数字(即:
  plus,minus,times,divide,zero,one) .例如 `IntField.( + )`
  不应该被直接定义为 `Stdlib.( + )`, 而是要用 `include` /
  functor的方式复用已有的定义.

- 有理数的strutures可以用一个简单的functor分别应用到 `IntField` /
  `FloatField` 来生成.

- 消除所有多余的 `of_int` 是可能的, 例如, 他被直接定义一次,
  其余的struct可以复用该定义.并且只在一个sig中直接声明它.
  这需要使用functor.
  还需要发明一种算法，可以将整数转换为任意环表示，而不管该环的表示类型是什么。

完成后，所有模块的类型应保持不变。可以通过运行 `ocamlc -i algebra.ml`
查看这些类型。

### 原始 `algebra.ml` 的类型:

``` ocaml
module type Ring =
  sig
    type t
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> t
  end
module type Field =
  sig
    type t
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val ( / ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> t
  end
module IntRing : Ring
module IntField : Field
module FloatRing : Ring
module FloatField : Field
module IntRational : Field
module FloatRational : Field
```

### 重构后的 `algebra.ml`

``` ocaml
module type RingWithoutOfInt = sig
  type t

  val zero : t

  val one : t

  val ( + ) : t -> t -> t

  val ( ~- ) : t -> t

  val ( * ) : t -> t -> t

  val to_string : t -> string

end

module AddOfInt (W: RingWithoutOfInt ) = struct
  include W 
  let of_int n =
    let rec loop acc = function
      |0 -> acc
      |num -> loop W. (one + acc ) (num-1)
    in loop W.zero n
end


module type Ring = sig
  include RingWithoutOfInt

   val of_int : int -> t    
end

module type Field = sig
  include Ring

  val ( / ) : t -> t -> t
end

module IntRingImpl  = AddOfInt( struct
  type t = int

  let zero = 0

  let one = 1

  let ( + ) = ( + )

  let ( ~- ) = ( ~- )

  let ( * ) = ( * )

  let to_string = string_of_int

end )


module IntRing : Ring = IntRingImpl 

module IntField : Field = struct
  include IntRingImpl
  let ( / )  =   ( / )
end

module FloatRingImpl  = AddOfInt (struct
  type t = float

  let zero = 0.

  let one = 1.

  let ( + ) = ( +. )

  let ( ~- ) = ( ~-. )

  let ( * ) = ( *. )

  let to_string = string_of_float

end) 

module FloatRing : Ring = FloatRingImpl 

module FloatField : Field = struct
  include FloatRingImpl
  let ( / ) = ( /. )
end

module ToRational (F:Field) : Field  =struct

  include AddOfInt(struct 
  type t = F.t * F.t
  let zero = (F.zero,F.zero)
  let one = (F.one ,F.one)
  let ( + ) ((a,b):t) ((c,d):t) =  F. ((a * d) + (c * b), b * d)
  let ( ~- ) ((a, b):t) = F. (-a, b)
  let ( * ) (a, b) (c, d) = F. (a * c, b * d)
  let to_string (a, b) = F.to_string a ^ "/" ^ F.to_string b 
end )

  let ( / ) ((a, b):t) ((c, d):t)  =F. (a * d, b * c)
end

module IntRational : Field  = ToRational(IntField)

module FloatRational : Field = ToRational(FloatField)

```

### `ocamlc -i algebra.ml` 的输出

``` ocaml
module type RingWithoutOfInt =
  sig
    type t
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
  end
module AddOfInt :
  functor (W : RingWithoutOfInt) ->
    sig
      type t = W.t
      val zero : t
      val one : t
      val ( + ) : t -> t -> t
      val ( ~- ) : t -> t
      val ( * ) : t -> t -> t
      val to_string : t -> string
      val of_int : int -> W.t
    end
module type Ring =
  sig
    type t
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> t
  end
module type Field =
  sig
    type t
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> t
    val ( / ) : t -> t -> t
  end
module IntRingImpl :
  sig
    type t = int
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> int
  end
module IntRing : Ring
module IntField : Field
module FloatRingImpl :
  sig
    type t = float
    val zero : t
    val one : t
    val ( + ) : t -> t -> t
    val ( ~- ) : t -> t
    val ( * ) : t -> t -> t
    val to_string : t -> string
    val of_int : int -> float
  end
module FloatRing : Ring
module FloatField : Field
module ToRational : functor (F : Field) -> Field
module IntRational : Field
module FloatRational : Field
```
