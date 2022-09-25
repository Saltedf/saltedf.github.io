#lang racket

; C-t new tab 
; C-r run the buffer 
#t
#f

"hello"
'sym  ; (quote sym)  don't eval it, just make it a symbol

4/3

(+ 1 3 ) ; plus is not an operator,
         ; it's just a function which doesn't need grammar to support 
(/ 14 3 3)

; type atom = Boolean | Number | Fraction | String | Symbol
; type s-expr = atom | s-list
; type s-list = "(" s-expr+ ")"
;
; type s-expr = atom | "(" s-expr+ ")" 

;; applicative order
(/ (+ 2 3)  1/3)
((λ (x) (* x x))  3)
;; 1. 符号 / 对应的函数
;; 2. 对每个参数进行求值
;; 3. 将函数应用到参数list上

;; 但程序中不全是 applictive order :
(define foo 1000) 
(if #t 'a (/ 1 0))

;; if/define不是函数, 而是一种特殊的形式  
;; 这些特殊形式/宏 不会对 "参数" 进行求值,其求值顺序不是applicative order
;; define 不会对 第一个"参数"进行求值 , 而只会对第二参数进行求值.
;; 而 if 是先对第一个参数进行求值, 并根据其求值结果来决定对第二/第三参数进行求值


;; Let -> "(" "let" Bindings Body ")"
;; Bindings -> "(" Binding ")"
;; Binding -> "[" symbol S-expr "]"
;; Body -> S-expr+

(let ([x 100]
      [y 200])
  (if (> x y) x y)
  )

;; let* 允许后面的绑定能使用前面定义过的绑定
;; let* 只是多个嵌套let的语法糖 
;; double-x 用到了 x 的绑定 

(let* ([x 100]
      [double-x (* 2 x)])
  (+ double-x x)
  )
;;;;;;;等价;;;;;;;
(let ([x 200])
  (let ([double-x (* 2 x)])
    (+ double-x x)
    ))

;; let 和 let* 都不能处理相互递归的定义
;; 因此需要用到 letrec
(letrec ([is-even? (λ (n)
                     (or (zero? n)
                         (is-odd? (sub1 n))))]
         [is-odd? (λ (n)
                    (and (not(zero? n))
                        (is-even? (sub1 n))))])

(is-even? 11))



;; (= 'a 'b)  error!!
;; = 用来比较数字 
(equal? 'a 'b)
(equal? 'hello 'hello)


;; Lambda -> "(" "lambda"  ArgList Body)
;; ArgList -> "(" s-expr* ")"
;; Body -> s-expr+

(define ident (lambda (x) x))
;; shortcut: ;;
(define (ident2 x) x)