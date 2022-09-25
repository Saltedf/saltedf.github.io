#lang racket
; C-t new tab 
; C-r reboot the repl

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


