# ch3

## list expressions

### 使用方括号来创建一个含有整数 1~5 的list

``` ocaml
[1;2;3;4;5] ;;
```

### 只用 `::` 和 `[]` 创建相同的list

``` ocaml
1::2::3::4::5::[] ;;
```

### 用 `@` 但不能用 `::` ，并用上 `[2;3;4]` 这个表达式来创建相同的list

``` ocaml
[1] @ [2;3;4] @ [5] ;;
```

## list的整数乘积

``` ocaml
let product lst =
  let rec product_tr acc = function 
    | [] -> acc 
    | h::t when h!=0 -> product_tr (h*acc) t
    | _ -> 0 
  in
  product_tr 1 lst
;;
```

## 连接list中的所有字符串

``` ocaml
let concat lst =
  let rec concat_tr acc = function
    |[] -> acc
    |h::t -> concat_tr (acc ^ h) t 
  in 
  concat_tr "" lst
;;
```

## 为product编写单元测试

``` ocaml
open OUnit2
open Product

let test_product = "test_product" >::: [
    "empty list" >:: (fun _ -> assert_equal 1 (product []) ) ;
    "one element" >:: (fun _ -> assert_equal 4 (product [4]) );
    "two elelemts" >:: (fun _ -> assert_equal 30 (product [5;6]) ) ;
    "contains zero" >:: (fun _ -> assert_equal 0 (product [0;34;54;12;1;3;5;6;] )  );
  ]


let _ = run_test_tt_main test_product
```

## 用模式匹配写下面三个函数

只要输入list满足性质就返回true,否则返回false

### list的首个元素是 “bigred”

``` ocaml
let func1 = function
  | h::_  when h = "bigred" -> true
  | _ ->false
;;
```

### list恰好有两个/四个元素（不能用length函数）

``` ocaml
let func2 = function
  | [_;_] ->  true
  | [ _;_;_;_] ->true
  | _ -> false
;;
```

### list的前两个元素是相等的

``` ocaml
let func3 = function
  | a::b::_ when a=b -> true
  | _ -> false
;;
```

## 用 `List` 标准库来解决问题：

### 编写一个接受 `int list` 的函数，它返回list的第五个元素

若list少于5个元素，则返回0 。 提示：用 `List.length` 和 `List.nth`

``` ocaml
let fifth  lst =
  if (List.length lst) < 5 then 0
  else List.nth lst 4
;;
```

### 编写一个接收 `int list` 的函数，它返回一个降序排列的list

提示：用 `List.sort` ，并用 `Stdlib.compare` 作为它的首个参数。以及使用
`List.rev` (反转list）

``` ocaml
let descend lst =
  lst |>  (List.sort Stdlib.compare)  |> List.rev
;;
```

## 分别为上面两个函数编写单元测试

``` ocaml
open Fifth
open OUnit2

let make_fifth_testcase name expect lst =
  name >:: (fun _ -> assert_equal  expect (fifth lst) )
;;

let fifth_test = "test suite of fifth" >::: [
    make_fifth_testcase "empty list" 0 [] ;
    make_fifth_testcase "lewer than five elements" 0 [1;3;4;5] ;
    make_fifth_testcase "exactly five elements" 5 [1;2;3;4;5] ;
    make_fifth_testcase "more then five elements" 5 [1;2;3;4;5;6] 
  ]

let _  = run_test_tt_main fifth_test 
```

``` ocaml
open OUnit2
open Descend

let make_descend_testcase name expect lst =
  name >:: (fun _ -> assert_equal expect (descend lst) ) 
;;

let descend_test_suite = "test descend" >::: [
    make_descend_testcase "empty list" [] [] ;
    make_descend_testcase "one element" [3] [3] ;
    make_descend_testcase "ascending list" [3;2;1] [1;2;3] 

  ]

let _ = run_test_tt_main descend_test_suite
```

## libray puzzle

解答只能是1-2行代码

### 编写一个返回list的最后一个元素的函数

函数应假定输入的list是非空的；提示用两个库函数，不要在代码中使用模式匹配

``` ocaml
let last_element lst =
  assert (lst != []) ; (List.nth lst  ((List.length lst) -1) )
;;
```

### 编写函数 any<sub>zeroes</sub> : int list -\> bool

此函数返回 true 当且仅当 输入list中至少有一个 0
提示：使用一个库函数，不要用模式匹配。

``` ocaml
let any_zeroes lst =
  List.mem 0 lst
;;
```

## take/drop

### 编写函数 `take:int-> 'a list->'a list`

使得 `take n lst` 返回lst的前n个元素。若lst少于n个元素，则返回整个list

``` ocaml
let take n lst =
  if (List.length lst) <= n then lst
  else
    let rec take_tr acc m l = match (m,l) with 
  | (0, _ )  -> List.rev acc 
  | ( _, h::t)  ->take_tr (h::acc)  (m-1) t
  | _ -> failwith "fail" 
    in
    take_tr [] n lst
;;
```

### 编写drop函数 `int -> 'a list -> 'a list`

满足 `drop n lit`
返回除了前n个之外的lst中剩下的元素。若lst少于n个元素，则返回空list

``` ocaml
let drop n lst =
  if (List.length lst) <= n then []
  else
    let rec drop_tr m l = match (m,l) with
  | (0,l) -> l
  | (i,h::t) -> drop_tr (m-1) t
  | _ -> failwith "something wrong"
    in
    drop_tr n lst
;;

```

## 将take/drop改写成尾递归的写法

并构造长list来测试这对两个函数的调用是否会导致栈溢出。

``` ocaml
let ( -- ) s e = 
  let rec from acc i j =
    if i > j then acc
    else  from  (j::acc) i (j-1)
  in
  from [] s e
;;
```

``` ocaml
let longlist = 1 -- 1000000 ;; 
```

## 是否为单峰list？

编写函数 `is_unimodal : int list -> bool`
,它接收一个整数list，并返回此列表是否为unimodal。 一个unimodal
list是一个list满足：存在一个元素，在之前的元素构成单调递增序列，在它之后的元素构成数组是单调递减的。
增长部分/减少部分都有可能是空的。由相同元素构成的list也是unimodal，空list也是。

``` ocaml
let  is_unimodal  lst =
  let rec impl  is_ascend_seg  l =
    match l with
    |[] -> true
    |[_] -> true
    (*下面的list模式表示 至少包含两个元素：*)
    |h::m::t when h=m  -> impl is_ascend_seg (m::t)  
    |h::m::t when h<m  -> if is_ascend_seg then impl true (m::t) else false
    |h::m::t (* when h>m *)-> impl false (m::t)
  in
  impl true lst
;;
```

## 幂集：全体子集构成的集合

编写函数 `powerset: int list -> int list list`
接收一个list作为一个集合，并返回此集合的“幂集”
（不用保持元素的顺序和输入list一致）

``` ocaml
let rec add_element acc e = function
  |[] -> acc
  |h::t ->  add_element ((e::h)::acc)  e t
;;

let rec powerset = function
  |[] -> [ [] ]
  |h::t -> let s = powerset t in (add_element [] h s ) @ s
;;
```

## print int list rec

编写函数 `print_int_list: int list -> unit` 使得：
将输入list的每个元素作为一行打印出来。 例如： `print_int_list [1;2;3]`
的输出是:

    1
    2
    3

基于下面的代码完成此函数：

``` ocaml
let rec print_int_list = function
| [] -> ()
| h :: t -> (* fill in here *); print_int_list t
```

``` ocaml
let rec print_int_list = function
  | [] -> ()
  | h :: t ->  print_endline (string_of_int h); print_int_list t
;;
```

## print int list iter

编写函数 `print_int_list' : int list -> unit`
其功能和上一题相同，但不能使用 `rec` 关键字，不过能使用标准库中的
`List.iter`

``` ocaml
let print_int_list' lst =
  List.iter (fun x -> (*fill in here*)  )  lst
;;
```

``` ocaml
let print_int_list' lst =
  List.iter (fun x ->  print_endline (string_of_int x)  )  lst
;;
```

## student 类型

``` ocaml
type student = {first_name : string ;last_name:string ;gpa :float}
;;
```

分别给出为下列类型的表达式：

### student

``` ocaml
{first_name= "salted" ;last_name="sun" ; gpa= 3.0} ;;
```

### student -\> string \* string 返回学生姓名

``` ocaml
let stu_name s =
  (s.first_name , s.last_name ) ;; 
```

### string -\> string -\> float -\> student 创建学生record

``` ocaml
 let init_stu_info f l g =
   {first_name=f;last_name=l ;gpa =g}
;;
```

## pokemon 类型

``` ocaml
type poketype = Normal | Fire | Water ;;
```

- 用record定义pokemon类型，有字段 name:string hp:int ptype:poketype

``` ocaml
type pokemon = { name:string; hp:int; ptype:poketype } ;;
```

- 创建一个名为 `charizard` 的pokemon, 其hp=78，为火属性。

``` ocaml
{name="charizard" ; hp=78; ptype = Fire };;
```

- 创建一个名为 `squirtle` 的pokemon，其hp=44，水属性。

``` ocaml
{name="squirtle" ; hp=44; ptype = Water };;
```

## 安全的hd/tl函数

``` ocaml
let safe_hd = function
  | [] -> None
  | h::t -> Some h
;;

let rec safe_tl = function
  | [] -> None
  | [x]-> Some x 
  | _::t ->  safe_tl t
;;;
```

## pokefun

编写函数 `max_hp: pokemon list-> pokemon option`
使得它返回hp最大的pokemon

``` ocaml
let max_hp_poke acc s =
 match (acc,s) with
   |(None, a) -> a
   |(a,None) -> a
   |(Some x,Some y) -> if x.hp>y.hp then Some x else Some y
;;

let max_hp lst =
  let rec impl acc  = function
  | [] -> acc 
  | h::t -> impl (max_hp_poke acc (Some h)) t  
  in
  impl None lst
;;
```

## date before

定义一个date-like三元组： `int*int*int` 一个日期类型是 date-like
三元组，其首个元素是正整数年份，第二个元素是1-12的月份，而三个元素是1-31的

编写函数 `is_before`
，它接收两个日期类型的参数，且若首个日期在第二个参数代表的日期的前面，则返回true.
否则将返回false 。

这个函数只能对合法日期是有效的，而不是任意的 date-like 类型。

``` ocaml
type date_like = int*int*int 

let is_leap_year y =
  if y mod 100 !=0 && y mod 4=0 then true
  else if y mod 400 = 0 then true
  else false


let is_valid_date  = function
  | (y,m,d)  when y <= 0 -> false  
  | (y,m,d) when m>12 || m<1 ->false
  | (y,m,d) when d>31 || d<1 ->false
  | (y,m,d) when  (is_leap_year y) && m = 2 && d >29  -> false 
  | (y,m,d) when  not (is_leap_year y) && m = 2 && d >28  ->false
  | (y,m,d) when  m mod 2=0 && d > 30  -> false
  | _ -> true


let is_before d1 d2 =
  if not (is_valid_date d1) || not (is_valid_date d2) then failwith "invalid date"
  else 
    match (d1,d2) with
    | ((y,m,d),(y1,m1,d1)) when y<y1 -> true
    | ((y,m,d),(y1,m1,d1)) when y=y1 && m<m1 -> true
    | ((y,m,d),(y1,m1,d1)) when y=y1 && m=m1 && d < d1 -> true
    | _ -> false
;;

```

## earliest date

编写函数 `earliest: (int*int*int) list -> (int*int*int) option` ，满足：

- 若输入list为空，则返回None
- 否则将返回list中最早的那个日期 Some date

（提示使用上一题中的 `is_before` )

``` ocaml

let earlier d1 d2 =
  match (d1,d2) with
  | (None,x) -> x
  |(x,None) -> x
  |(Some a,Some b)-> if is_before a b then Some a else Some b



 let rec earliest lst  =
   let rec impl acc = function
   |[] -> acc
   |h::t -> impl (earlier (Some h) acc) t  
   in
   impl None lst
 ;;
```

## assoc list

``` ocaml
let insert k v lst = (k,v)::lst

let rec lookup key = function
  | [] -> None
  | (k,v)::t -> if k = key then v else lookup key t
;;
```

用上面这两个函数构造一个 association list，满足：
将数字1映射为"one",2映射为"two", 3映射为"three"
并且用key=2,和key=4进行查询。

``` ocaml
let numlist = [] ;;

insert 1 "one" numlist;;
insert 2 "two" numlist;;
insert 3 "three" numlist;;

lookup 2 ;;
lookup 4 ;;

```

## cards

``` ocaml
type suit = Clubs | Diamonds | Hearts | Spades ;; (*花色*)

type rank =
  One | Two | Three | Four | Five | Six |Seven | Eight |Nine |Ten |Jack | Queen| King|Ace
;; (* 点数 *)

type card =
  { suit:suit ; rank:rank} ;;

{ suit = Clubs ; rank=Ace } ;;
{ suit = Hearts; rank=Queen};;
{ suit = Diamonds; rank= Two};;
{ suit = Spades ; rank = Seven};;



```

## matching

为下面的每个模式，给出一个类型为 `int option list`
的值，使得它不能匹配上模式，并且它不是空list.
若找不到这样的值则解释为什么。

- Some x::tl

``` ocaml
[None; Some 1] ;;
```

因为此模式要求以某个形如Some x开头的list

- \[Some 3110;None\]

此模式只能和 \[Some 3110 ; None\]相匹配

``` ocaml
[Some 2110;None] ;;
```

- \[Some x; \_\]

``` ocaml
[None;Some 2];;
```

- h1::h2::tl 此模式表示list中至少有两个元素

``` ocaml
[Some 1 ] ;;
```

- h::tl

不能和此模式匹配的值仅有 \[\] 。因为此模式表示list中至少有一个元素。

## quadrant 象限

完成下面的象限函数，它能返回给定一点(x,y)所在的象限。
约定在坐标轴上的点不属于任何象限。
（提示：a.定义helper函数来返回整数的符号 b. 匹配pair）

``` ocaml
  type quad = I | II | III | IV
  type sign = Neg | Zero | Pos
;;
  let sign (x:int) : sign =
    ...

  let quadrant : int*int -> quad option = fun (x,y) ->
    match ... with
  | ... -> Some I
  | ... -> Some II
  | ... -> Some III
  | ... -> Some IV
  | ... -> None

```

解答：

``` ocaml
let sign (x:int) :sign =
  match x with
  |i when i> 0 -> Pos
  |i when i<0 -> Neg
  | _ -> Zero


let quadrant: int*int -> quad option = fun (x,y)  ->
  match (sign x , sign y) with
  |(Pos,Pos) -> Some I
  |(Neg ,Pos) -> Some II
  |(Neg,Neg) -> Some III
  |(Pos,Neg) -> Some IV
  |_ -> None
;;
```

## 使用 when 重写quadrant函数

不能用上一问的辅助函数

``` ocaml
let quadrant' : int*int -> quad option = fun (x,y)  ->
   match (x , y) with
     |(a,b) when a>0&& b>0 -> Some I
     |(a,b) when a<0&& b>0 -> Some II
     |(a,b) when a<0&& b<0 -> Some III
     |(a,b) when a>0 && b<0 -> Some IV
     |_-> None
;;
```

## depth

编写函数 `depth: 'a tree -> int` 返回从根到叶子节点的最长路径（节点个数)
例如，空tree（Leaf）的深度为0 (提示 可以使用库函数 `max` )

``` ocaml

type 'a tree = Leaf | Node of 'a * 'a tree * 'a tree ;;

let rec depth = function
  | Leaf -> 0
  | Node (v,left,right) -> 1 + (max (depth left) (depth right) )
;;

```

## shape

编写函数 `same_shape: 'a tree -> 'b tree -> bool`
，它能判断两个tree是否有相同的形状，忽略在对应节点处的值的不同。
提示：使用带有三个分支的模式匹配，被匹配的表达式是一对trees

``` ocaml
let rec  same_shape (ta:'a) (tb:'b) : bool = match (ta,tb) with
  |(Leaf,Leaf) -> true 
  |( (Node(_,la,ra)) ,(Node(_,lb,rb))) ->  (same_shape la lb) &&( same_shape ra rb)
  | _ -> false
;;
```

``` ocaml
let ta = Node(2,Node(1,Leaf,Leaf) ,Node(3,Leaf,Leaf) ) 
let tb = Node (2. ,Node(1.,Leaf,Leaf) ,Node (3.,Leaf,Leaf) ) ;;
```

``` ocaml
same_shape ta tb ;;
- : bool = true
```

## list max exn

编写函数 `list_max: int list -> int`
它返回list中的最大整数；若list为空则引发异常 `Failure "list_max"`

``` ocaml
  let rec list_max = function 
  |[x] -> x
  |h::t -> max h (list_max t)
  | _ -> failwith "list_max" 
;;
```

## list max exn string

编写函数 `list_max_string: int list -> string`
，它返回一个包含list中最大整数的字符串。若list为空，则返回"empty"字符串。
提示： 可以用库函数 `string_of_int`

``` ocaml
let list_max_string : int list -> string = fun lst ->
  try string_of_int (list_max lst) with
  |_ -> "empty"
;;
```

## list max exn ounit

编写两个OUnit测试来检测函数：list max exn
是否在list为空时正确地引发了异常，以及在list不空时返回了list中的最大值。

``` ocaml
open OUnit2

let rec list_max = function 
  | [x] -> x 
  | h::t -> max h (list_max t) 
  | _ -> failwith "list_max"
;;


let test_list_max = "list_max" >::: [
    "empty list" >:: (fun _ -> assert_raises (Failure "list_max") (fun () -> list_max []) ) ;
    "nonempty list" >:: (fun _ -> assert_equal 3 (list_max [1;2;3;1] )) 
  ]

let _ = run_test_tt_main test_list_max ;;

```

## 用二叉搜索树实现字典

回顾实验 assoc list，用关联列表来实现字典
，其插入函数是常数时间，但查找要花费线性时间。

有更高效的字典实现：使用二叉搜索树 。 树的每个节点将是一对键和值，
就像在关联列表中一样。 此外，树满足二叉搜索树不变量 ：对于任何节点
n，所有 n 的左子树中的值具有小于 n 的键， 并且 n
的右子树中的所有值都有键 大于 n 的key。 （不允许重复键。）

例：

``` ocaml
let d = 
  Node((2,"two"), 
    Node((1,"one"),Leaf,Leaf),
    Node((3,"three"),Leaf,Leaf)
  )
```

用二叉搜索树实现字典 :

### 查找 \[✭✭\]

写一个函数 `lookup : 'a -> ('a*'b) tree -> 'b option`
返回与给定键关联的值（如果存在）。

``` ocaml
let rec lookup key = function
  | Node( (k,v), _,_ ) when k= key -> Some v
  | Node( (k,_), l,_ ) when k > key -> lookup key l
  | Node( (k,_), _,r ) when k < key -> lookup key r
  | _ -> None
;;
```

### 插入 \[✭✭✭\]

写一个函数 `insert : 'a -> 'b -> ('a*'b) tree -> ('a*'b) tree`
它将新的键值映射添加到给定的二叉搜索树。 如果钥匙
已经映射到树中，输出树应该将键映射到 新的价值。

``` ocaml
  let rec insert key value = function
    | Node( (k,v),l,r) when k = key -> Node((key,value),l,r)
    | Node( (k,v),l,r) when k > key -> Node((k,v), (insert key value l) , r)
    | Node( (k,v),l,r) when k < key -> Node((k,v), l , (insert key value r) )
    | _  -> Node( (key,value),Leaf,Leaf) 
;;
```

``` ocaml
let dict = insert 3 "three" (insert 1 "one"  (insert 2 "two" dict)) ;;

 - : (int * string) tree =
 Node ((2, "two"), Node ((1, "one"), Leaf, Leaf),
   Node ((3, "three"), Leaf, Leaf))
```

### `is_bst` \[✭✭✭✭\]

编写函数 `is_bst: ('a * 'b) tree -> bool`
，它返回true当且仅当给定的tree满足二叉搜索树的性质。
此函数的一个高效版本是最多访问每个节点一次。

1.  提示

    编写一个递归的辅助函数，它接收一个tree，返回下面三者之一：

    \(i\) tree中的最小值和最大值

    \(ii\) 若tree为空，则返回这个信息

    \(iii\) 返回这个tree不是二叉搜索树

    `is_bst`
    函数不可以是递归的，但它可以调用辅助函数，并在其返回结果上进行模式匹配。
    需要为辅助函数的返回类型定义一个变体variant类型。

2.  solution

    ``` ocaml

    type 'a bst_return = Empty | NotBst | Bst of { min:'a; max: 'a}  ;;

    let rec helper get_key = function
      | Leaf -> Empty
      | Node(v,Leaf,Leaf) -> Bst {min=get_key v;max=get_key v} 
      | Node(v,Node(lv,_,_),Node(rv,_,_)) when get_key v <= get_key lv || get_key v >= get_key rv -> NotBst
      | Node(v,l,r )  ->
        begin
      match (helper get_key l , helper get_key r ) with
      | ( Bst{min=lmin;max=lmax}, Bst{min=rmin;max=rmax}) -> Bst{min=(min lmin rmin) ;max=(max lmax rmax)}
      | ( Bst{min=lmin;max=lmax},Empty ) -> Bst{min=lmin;max=lmax}
      | ( Empty ,Bst{min=rmin;max=rmax}) -> Bst{min=rmin;max=rmax}
      | _ -> NotBst
        end
    ;;

    let is_bst dict =
      let get_key = (fun (x,y) -> x ) in
      match helper get_key dict with
      | NotBst -> false
      | _ ->true
    ;;


    ```

## quadrant poly (使用匿名Variant重写）

``` ocaml
val sign : int -> [> `Neg | `Pos | `Zero ]
val quadrant : int * int -> [> `I | `II | `III | `IV ] option
```

``` ocaml
let sign = function
  |i when i>0 -> `Pos
  |i when i=0 -> `Zero
  |_ -> `Neg
;;

let quadrant (x,y) = match (sign x,sign y) with
  |(`Pos,`Pos ) -> Some `I
  |(`Neg,`Pos ) -> Some `II
  |(`Neg,`Neg ) -> Some `III
  |(`Pos,`Neg ) -> Some `IV
  | _ -> None 
;;
```
