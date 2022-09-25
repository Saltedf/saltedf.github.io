(** 
   [map]:
   ( some parser |> (map f:对前一个parse的结果进行映射) )  "some input"
   
   [bind]:
   ( some-parser |> (bind f:根据前一个parser结果返回某个特定的parser,然后继续用得到的parser进行解析 ) )  "some input" 
*)
type input_st = {
  text : string ;
  index : int; 
}

type error_msg = {
  msg : string ;
  index : int ;
}

(** [parser] : input_state -> Ok (result, new_input_state) / Error error_msg  *)
type 'a parser =  input_st ->  ('a * input_st,  error_msg ) result

let eof = fun input_st ->
  if String.length input_st.text <= input_st.index
  then Ok("EOF",input_st)
  else Error{msg =(Printf.sprintf "excepted `EOF`,but met `%s`"  (Str.string_after input_st.text input_st.index ) )
            ;index = input_st.index} 
    
let str (s:string) = fun input_st ->
  if Str.string_match (Str.regexp s) input_st.text input_st.index
  then
    let matched =  Str.matched_string input_st.text  in 
    let matched_len = String.length matched in
    Ok (matched ,{input_st with index = input_st.index + matched_len })
  else 
    Error {msg = (Printf.sprintf "excepted `%s`,but met `%s`" s (Str.string_after input_st.text input_st.index ) ) ;
           index = input_st.index }


(* ================================================================ *)

let map (res_to_res : 'a -> 'b )  (prev : 'a parser ) : 'b parser =
  fun input_state -> match prev input_state with 
    | Ok (res,rest) -> Ok (res_to_res res , rest) 
    | Error e -> Error e  

let (==>) p f  = map f p

let bind (res_to_p: 'a -> 'b parser ) (prev : 'a parser) : 'b parser =
  fun input_state ->  match prev input_state with
    | Ok (res, rest ) ->  (res_to_p res) rest 
    | Error e -> Error e 

let (>>>) p pf  = bind pf p 



(**
   [p1 *> p2 "some input"]
   ignore the parsing results of p1, and pass the input_state in the output of p1 to p2
    ( p2's result, the input state after parsing by p1 and p2)
*)
let ( *> ) p1 p2 =
  fun input_st -> match p1 input_st with
    | Ok (_, rest) -> p2 rest 
    | Error e -> Error e 



(**
   [p1 <* p2 "some input"]
   ignore the parsing results of p2, only retain the input state after p2 parsing.
    (p1's result , the input state after parsing by p1 and p2)
*)
let ( <* ) p1 p2 = fun input_st -> match p1 input_st with
  | Ok(r1, rest1) ->
    begin  match p2 rest1 with
      | Ok (_, rest2) -> Ok (r1,rest2)
      | Error e -> Error e 
    end
  | Error e -> Error e 


(**
   [p1 <*> p2 input]
   ( (p1's result,p2's result), the input state after parsing by p1 and p2)
*)
let ( <*> ) p1 p2 =  (* fun input_st -> *)
  p1 |>  bind (fun r -> p2  |> map (fun r2 -> (r,r2) ) ) 
  
  (* match p1 input_st with
   * | Ok(r1, rest1) ->
   *   begin   match p2 rest1 with
   *     | Ok (r2, rest2) -> Ok ((r1,r2) ,rest2)
   *     | Error e -> Error e 
   *   end
   * | Error e -> Error e  *)
let zero_or_one p = fun input_st ->
  match p input_st with
  |Ok (res,rest) ->  Ok([res],rest)
  |Error _ -> Ok( [] ,input_st)
   

let many p : 'b parser  =
let rec loop acc =  fun input_st ->
  match p input_st with
  | Ok(r,rest) ->   loop (acc @ [r])   rest
  | Error e -> Ok(acc, input_st) 
in
loop [] 


let ( <|> ) (p1: 'a parser) (p2: 'b parser) : 'c parser  =
  fun input_st ->
  match p1 input_st with
  | Ok (r1,rest) ->  Ok (r1,rest)
  | Error e1 ->
    begin
      match p2 input_st with
      | Ok (r2,rest) -> Ok (r2,rest)
      | Error e2 -> Error {msg = Printf.sprintf "%s OR %s" e1.msg e2.msg ;index = e1.index }
    end
 
      
let notmatch init (p:'b parser)  : 'a parser = fun st ->
  match p st with
  |Ok (_ ,_) -> Error {msg = " ";index = st.index}
  |Error _-> Ok (init,st)


let spaces = str "[ \t\r\n\f]+"

let line_comment = str "//[^\n\r]*\\(\n\\|\n\r\\|\r\\)?"

let start_block_comment = str "/\\*" 


(* let in_block_comment = str "[^\\(\\)]*" *)
    
let rec end_block_comment st = ( (str "\\*/") <|> (str "[^\\(\\)]" *> end_block_comment) ) st  

let block_comment =  start_block_comment  *> end_block_comment (* ==> (fun _ -> "block comment") *)  

let something_to_ignore (par: 'a parser) : 'a parser =  ( many(spaces <|> line_comment <|> block_comment ) ==> (fun _ -> "")  ) *> par <* ( many(spaces <|> line_comment <|> block_comment ) ==> (fun _ -> "")  )
                                                                                                                                          
let start_string =  str "\""

let in_string  = many ((str "[^\\\"\n\r]+")  <|> (str "\\[0-7][0-7][0-7]") <|>  (str "\\[^\\(\\)]")  )

  (* (str "\\(\\(\\\\\"\\)\\|[^\"]\\)*")  *)

let end_string =   str "\"" 

let string_literal = ( start_string *> in_string  <*  end_string  ) |> something_to_ignore 


let in_char = (str "[^'\\\n\r]")  <|> (str "\\[0-7][0-7][0-7]") <|>  (str "\\[^\\(\\)]") 
let char_literal = (str "'"  *> in_char <* str "'" ) |> something_to_ignore   



(* type keywords = Void | Char | Short | Integer | Long | Struct | Union | Enum | Static | Extern | Const | Signed | Unsigned | If | Else | Switch | Case | Default | While | Do | For  *)

let voidp  =  str "void"  |> something_to_ignore 
let charp = str "char" |> something_to_ignore 
let shortp =  str "short"|> something_to_ignore 
let intp = str "int" |> something_to_ignore 
let longp = str "long" |> something_to_ignore  
let structp  = str "struct" |> something_to_ignore  
let unionp = str "union" |> something_to_ignore  
let enump = str "enum" |> something_to_ignore  
let staticp = str "static" |> something_to_ignore  
let externp = str "extern" |> something_to_ignore  
let constp = str "const" |> something_to_ignore  
let signedp = str "signed" |> something_to_ignore  
let unsignedp = str "unsigned" |> something_to_ignore  
let ifp = str "if" |> something_to_ignore  
let elsep = str "else" |> something_to_ignore  
let switchp = str "switch" |> something_to_ignore 
let casep = str "case" |> something_to_ignore 
let defaultp = str "default" |> something_to_ignore 
let whilep = str "while" |> something_to_ignore 
let dop = str "do" |> something_to_ignore 
let forp = str "for" |> something_to_ignore 
let returnp = str "return" |> something_to_ignore 
let breakp = str "break" |> something_to_ignore 
let continuep = str "continue" |> something_to_ignore 
let gotop = str "goto" |> something_to_ignore 
let typedefp = str "typedef" |> something_to_ignore 
let importp = str "import"  |> something_to_ignore 
let sizeofp = str "sizeof" |> something_to_ignore 

let identifier = str "[a-zA-Z_][a-zA-Z_0-9]*"  |> something_to_ignore 

let integer = ((str "[1-9][0-9]*[U]?[L]?" )
              <|> (str "0[xX][0-9a-fA-F]+[U]?[L]?")
              <|> (str "0[0-7]*[U]?[L]?") )  |> something_to_ignore 




type oper = Plus | Minus | Times| Div | Equal | NotEqual | GreaterThen |GreaterOrEqual | LessThen | LessOrEqual | Assign 
let to_oper = function
  | "+" -> Plus
  | "-" -> Minus
  | "*" -> Times
  | "/" -> Div
  | "==" -> Equal 
  | "!=" -> NotEqual
  | ">" -> GreaterThen
  |">=" -> GreaterOrEqual
  | "<" -> LessThen
  | "<=" -> LessOrEqual
  | "=" -> Assign 
  |  x -> failwith ("unknown " ^ x)

type node =
    None
  | Literal of string
  | Opnode of {op :oper ;left: node ;right: node }
                                               
let times_or_div =  (str "*" <|> str "/")  |> something_to_ignore
let plus_or_minus =  (str "+" <|> str "-")  |> something_to_ignore

  

(* let rec fp  st= ((identifier <|> integer )  ==> (fun r -> Literal r )) st 
 * 
 * and tp st = ( (fp <* (notmatch (Literal "") times_or_div)) <|>
 *              (tp >>> (fun left -> times_or_div >>> (fun op -> fp ==> (fun right -> Opnode (to_oper(op),[left;right] ) ) )))
 *             ) st
 * and ep st = (
 *  ( tp <* (notmatch (Literal "") plus_or_minus) ) <|>
 *  ( ep >>> (fun left -> plus_or_minus >>> (fun op -> tp ==> (fun right -> Opnode(to_oper(op),[left;right])))))
 * ) st *)

 


(* let rec  factor  st = ( (integer ==> (fun r -> Literal r )) <|>  (str "(" *>  expr  <* str ")" ) ) st
 *     
 * and  unary st =  (zero_or_one( str "+"<|> str "-"  ) >>> (fun s -> factor ==> (fun f -> match (s,f) with
 *     | (["-"] , Literal n) ->  Literal ( (int_of_string n)*(-1) |> string_of_int )
 *     | (["-"] , Opnode x) -> Opnode {op=Times;left = Literal "-1";right = Opnode x}
 *     | (_,nod) -> nod 
 *   ) ) ) st 
 *   
 * and divide_sth st  =( str "/" >>> (fun op -> unary ==> (fun rest -> Opnode { op=to_oper(op);left = None ;right = rest   })) ) st
 * 
 * and times_sth st = ( str "*" >>> (fun op -> unary  ==> (fun rest -> Opnode { op=to_oper(op);left = None ;right = rest } )) ) st
 * 
 * and times_divide_seq  st = (many( divide_sth <|> times_sth) ==> (fun lst -> match List.rev lst with
 *     | [] -> None 
 *     | h::t ->  List.fold_left  (fun acc e -> let Opnode a = acc in  Opnode {a with left = e} ) h t) ) st 
 * 
 * and  add_to_leftmost e tree =
 *   match tree with
 *   |Opnode {op=o;left=l;right=r} ->  Opnode{op=o;left= (add_to_leftmost e l);right =r} 
 *   | _ -> e
 *   
 * and  term st = (unary  >>> (fun left -> times_divide_seq ==> (fun tree -> add_to_leftmost left tree ) )) st
 * 
 * and  plus_sth st = (str "+" >>> (fun op -> term ==> (fun rest -> Opnode { op=to_oper(op);left = None ;right = rest   }))) st
 * 
 * and minus_sth st =( str "-" >>> (fun op -> term  ==> (fun rest -> Opnode { op=to_oper(op);left = None ;right = rest } ))) st 
 * 
 * and plus_minus_seq st = (many( plus_sth <|> minus_sth) ==> (fun lst -> match List.rev lst with
 *     | [] -> None 
 *     | h::t ->  List.fold_left  (fun acc e -> let Opnode a = acc in  Opnode {a with left = e} ) h t) ) st
 * 
 * and relational_rest st = ((str ">=" <|> str ">" <|> str "<=" <|> str "<") >>> (fun o ->  term ==> (fun r ->  Opnode {op=to_oper(o);left =None;right = r }) ) ) st
 * and relational_rest_seq  st =( many(relational_rest) ==> (fun lst -> match List.rev lst with
 *     | [] -> None
 *     |h::t ->  List.fold_left  (fun acc e -> let Opnode a = acc in  Opnode {a with left = e} ) h t) ) st 
 * and  relational st  =( term >>> (fun left -> plus_minus_seq ==> (fun tree -> add_to_leftmost left tree))   ) st
 *     
 * and equality_rest st = ( (str "==" <|> str "!=") >>> (fun o -> relational ==> (fun r ->
 *   Opnode{op= to_oper(o);left = None ;right =r  }) ) ) st
 * 
 * and equality_rest_seq  st =   ( many(equality_rest) ==> (fun lst -> match List.rev lst with
 *     | [] -> None
 *     |h::t ->  List.fold_left  (fun acc e -> let Opnode a = acc in  Opnode {a with left = e} ) h t) ) st 
 * and equality st = (relational >>>(fun left -> relational_rest_seq ==> (fun tree -> add_to_leftmost left tree) )) st
 * and assign st = ( (equality ) <|> (equality >>> (fun l -> str "=" >>> (fun a -> assign ==> (fun r -> Opnode{ op=Assign; left=l;right= r } )))) ) st
 * 
 * and expr st =  assign st
 * and stmt  st= (expr <* str ";") st
 * and program st = ( many(stmt) <* eof ) st 
 * (\*and  expr st = (equality >>> (fun left -> equality_rest_seq  ==> (fun tree -> add_to_leftmost left tree ) )) st   *\) *)


(*======================*)


let rec primary st  = ((( identifier <|> integer) ==> (fun r -> Literal r ) ) <|>   (str "(" *>  expr  <* str ")" ) )  st

and unary st =   (zero_or_one( str "+"<|> str "-"  ) >>> (fun s -> primary  ==> (fun p -> match (s,p) with
    | (["-"] , Literal n) ->  Literal ( (int_of_string n)*(-1) |> string_of_int )
    | (["-"] , Opnode x) -> Opnode {op=Times;left = Literal "-1";right = Opnode x}
    | (_,nod) -> nod 
  ) ) ) st 
and mul st = ( 
  ( unary >>> (fun l -> (str "*"<|> str "/") >>> (fun o -> unary ==> (fun r -> Opnode{op=to_oper(o);left = l ;right = r }))) )
  <|> unary 
) st
and add st =  ( 
  (mul >>> (fun l -> (str "+"<|> str "-") >>> (fun o -> mul  ==> (fun r -> Opnode{op=to_oper(o);left = l ;right = r }))) )
  <|> mul 
) st


and relational st =  (
  (add  >>> (fun l -> (str ">"<|> str ">="<|>str "<" <|> str "<=" ) >>> (fun o -> add  ==> (fun r -> Opnode{op=to_oper(o);left = l ;right = r }))) ) <|> add 
) st

and equality st =   (
  (relational  >>> (fun l -> (str "=="<|> str "!=") >>> (fun o -> relational  ==> (fun r -> Opnode{op=to_oper(o);left = l ;right = r }))) ) <|> relational 
) st
              
and assign st = (
  ( equality >>> (fun l -> str "=" >>>(fun a -> assign ==> (fun r -> Opnode {op=Assign;left =l;right= r}))  ))
 <|> equality 
             ) st

and expr st = assign st
and stmt st = (expr <* str ";") st
and program st =( many(stmt) <* eof ) st 
  
let get_node res =  res |> Result.get_ok |> fst  

let gen_init ()  =
  Printf.printf ".intel_syntax noprefix\n";
  Printf.printf ".globl main\n";
  Printf.printf "main: \n" 

let rec gen_expr n =
  
 match n with
   | Literal s -> Printf.printf "  push %s\n" s
   | Opnode {op=o;left=l;right=r} when o = Assign ->
     begin
       failwith "TODO: assign" 
     end 
  | Opnode {op=o;left=l;right=r} -> 
    begin 
      let () = gen_expr l in
      let () = gen_expr r in
      let _ = Printf.printf "  pop rdi\n" in
      let _ = Printf.printf "  pop rax\n" in 
      (match o with
       | Plus ->  Printf.printf "  add rax, rdi\n" 
       | Minus -> Printf.printf "  sub rax, rdi\n" 
       | Times -> Printf.printf "  imul rax, rdi\n" 
       | Div  ->  Printf.printf "  cqo\n  idiv rdi\n"
       | Equal -> Printf.printf "  cmp rax, rdi\n";Printf.printf "  sete al\n";Printf.printf "  movzb rax,al\n"
       | NotEqual -> Printf.printf "  cmp rax, rdi\n";Printf.printf "  setne al\n";Printf.printf "  movzb rax,al\n"
       | LessThen -> Printf.printf "  cmp rax, rdi\n";Printf.printf "  setl al\n";Printf.printf "  movzb rax,al\n"
       | LessOrEqual -> Printf.printf "  cmp rax, rdi\n";Printf.printf "  setle al\n";Printf.printf "  movzb rax,al\n"
       | GreaterThen -> Printf.printf "  cmp rdi, rax\n";Printf.printf "  setl al\n";Printf.printf "  movzb rax,al\n"
       | GreaterOrEqual -> Printf.printf "  cmp rdi, rax\n";Printf.printf "  setle al\n";Printf.printf "  movzb rax,al\n"
      ); 
      Printf.printf "  push rax\n" 
    end
  | _ -> failwith "empty node"

let gen_ret () =  Printf.printf "  pop rax\n  ret\n"

let compile input =
  gen_init() ;
  {text= input;index = 0} |> expr |> get_node |> gen_expr ;
  gen_ret () 







