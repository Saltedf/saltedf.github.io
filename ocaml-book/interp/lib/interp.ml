
type op = Func of string
        | Plus

type atom = Int of int 
type sexp =Exp of  op * int list
          | Atom of atom 

type args = int list


type ('a ) defines =
  | Deffun of string * args * sexp list
  | Defvar of string * sexp 

type ('a) start = Start of 'a defines

type sexp = Single of keywords *  num * num
           | Mult of keywords * sexp * sexp 
            

  let interp e = match e with
    | (Begin,e1,e2) ->
    | exp ->  


  
