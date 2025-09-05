# [ch2 ex](https://cs3110.github.io/textbook/chapters/basics/exercises.html)

## values

``` ocaml
utop # 7* (1+2+3) ;;
- : int = 42

utop # "CS " ^ string_of_int 3110 ;; 
- : string = "CS 3110"
```

## operators

``` ocaml
utop # 42 * 10 ;;
- : int = 420

utop # 3.14 /. 2.0 ;;
- : float = 1.57


utop # 4.2 *. 4.2 *. 4.2 *. 4.2 *. 4.2 *. 4.2 *. 4.2 ;;
- : float = 23053.933324800008
```

## equality

``` ocaml
utop # 42 = 42 ;;
- : bool = true

utop # "hi" = "hi" ;;  structural equality
- : bool = true

utop # "hi" == "hi" ;;  physical equality :compare pointers/addresses
- : bool = false
```

## assert

``` ocaml
utop # assert true ;;
- : unit = ()
```

``` ocaml
utop # assert false ;;

Exception: "Assert_failure //toplevel//:1:0"
Called from Stdlib__Fun.protect in file "fun.ml", line 33, characters 8-15
Re-raised at Stdlib__Fun.protect in file "fun.ml", line 38, characters 6-52
Called from Topeval.load_lambda in file "toplevel/byte/topeval.ml", line 89, characters 4-150
```

``` ocaml
utop # assert (2110 != 3110 );;
- : unit = ()
```

## if

``` ocaml
utop # if 2 > 1 then 42 else 7 ;;
- : int = 42
```

## double fun

``` ocaml
let double x = 2 * (x) ;;

assert ( (double (-100)) = (-200)) ;
assert ( 1 =  (double 0));
assert ( 46 = (double 23)) ;;
```

## more fun

### cube

``` ocaml
let cube x : float  = x *. x *. x ;;
```

### sign

``` ocaml
let sign x : int  =
  if x > 0 then 1
  else if x = 0 then 0
  else -1
;;
```

### the area of a circle

``` ocaml
let area_of_circle r : float =
  if r < 0. then failwith "r<0" ;
  ( 3.1415926 *. r *.  r)
;;

let absf x :float =
  if x >= 0. then x
  else (-1.) *.  x
;;

(** [r] is the raduis of a circle *)
let test_area_of_circle r expected_area =
  assert (absf ((area_of_circle r) -.  expected_area) < 0.01 )
;;

test_area_of_circle 2. 12.56 ;;
```

## RMS 均方根

``` ocaml
let rms x y =  sqrt @@ (x *. x +. y *. y) /. 2. ;;
```

## date fun

``` ocaml
(** [m] should be a month. [d] is day.
    if [m] and [d] is a valid date, then returns true *)
let date (m:string) ( d:int)  =
  if (  m = "Jan" && d>=1 && d <= 31
  || m= "Feb" && d>=1 && d <=28
  || m = "Mar" && d>=1 && d <= 31
  || m = "Apr" && d>=1 && d < 31
  || m = "May" && d>=1 && d <= 31
  || m = "Jun"  && d>=1 && d < 31
  || m = "Jul" && d>=1 && d <= 31
  || m = "Aug" && d>=1 && d < 31
  || m = "Sept" && d>=1 && d <= 31
  || m = "Oct" && d>=1 && d < 31
  || m = "Nov" && d>=1 && d <= 31
  || m = "Dec" && d>=1 && d < 31 )
  then true 
  else false
;;

```

## fib

``` ocaml
  let rec fib n =
    if n = 1 then 1
    else if n = 2 then 1
    else fib (n-1) + fib (n-2)
;;
```

## fib fast

``` ocaml
let rec helper  nstep pp p =
  if nstep = 1 then p
  else helper (nstep-1) p (pp+p )
;;

let fib_fast n = helper n 0 1 ;;
```

## func type

``` ocaml
let f x = if x then x else x  (* bool -> bool *)
let g x y = if y then x else x  (* 'a -> bool -> 'a *)
let h x y z = if x then y else z  (* bool -> 'a -> 'a -> 'a *)
let i x y z = if x then y else y  (* bool -> 'a -> 'b -> 'a *)
```

## divide

Write a function divide : numerator:float -\> denominator:float -\>
float. Apply your function.

``` ocaml
let divide numerator denominator =
  if (denominator = 0.) then failwith "divide 0" ;
  numerator /. denominator
  ;;
```

## associativity

Suppose that we have defined let add x y = x + y. Which of the following
produces an integer, which produces a function, and which produces an
error? Decide on an answer, then check your answer in the toplevel.

``` ocaml
add 5 1  --> int
add 5    --> func
(add 5) 1 --> int
add (5 1) --> error
```

## average

Define an infix operator +/. to compute the average of two
floating-point numbers. For example,

1.0 +/. 2.0 = 1.5

1.  +/. 0. = 0.

``` ocaml
let ( +/. ) a b =
 ( a +. b) /. 2.0
;;
```

## hello world

print<sub>endline</sub> "Hello world!";;

print<sub>string</sub> "Hello world!";;

``` ocaml
print_string "hello world" ;;
hello world- : unit = ()

print_endline "hello world" ;;
hello world
- : unit = ()
```
