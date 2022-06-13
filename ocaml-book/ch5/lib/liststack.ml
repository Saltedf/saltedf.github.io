type 'a stack = 'a list * int 
exception StackIsEmpty

let empty = ([],0) 
let is_empty = function
  | ([],_) -> true
  | _ -> false
let size (_,n) = n 
let push e (s,n) = (e::s, (1+n) ) 
let peek = function
  | ([],_) -> raise StackIsEmpty
  | (h::_,_ ) -> h 
let pop = function
  | ([],_) -> raise StackIsEmpty
  | (_::t,n) -> (t,(n-1))


Map.Make()
