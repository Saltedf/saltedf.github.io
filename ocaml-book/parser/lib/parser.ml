
type  res = Str of string | Integer of int | Float of float  | Pair of string * res  |  Lst of res list 

let get_str  = function
  | Str s -> s
  | _ ->  failwith "result should be a Str _" 

let get_pair_fst  = function
  | Pair (name , _) -> name 
  | _ -> failwith "the result should be a Pair"
           
let get_pair_snd  = function
  | Pair (_ , e) -> e
  | _ -> failwith "the result should be a Pair"

let compose  f g  x = f (g x)
let ( |=> ) g f = compose f g


(** [pstate] means parser state *)
type 'a pstate  = 
  {
    iserror : bool ;
    error : string ;
    result : res ;
    targetstr: 'a  ;
    index : int; 
  }

let  append_element (e:res ) lst =
  let rec impl acc  = function
  | [] -> List.rev (e::acc)
  | h::t -> impl (h::acc) t
  in impl [] lst 

let rest_input st  =
  try Str.string_after st.targetstr st.index
  with
  | _ -> ""
    
    
let is_end st = (String.length (rest_input st) ) = 0

let update_state st res idx =
  { iserror = false ; error = "" ; result = res ; targetstr = st.targetstr ; index = idx  }
  
let update_state_result st res = { st with result = res}
                                   
let update_state_when_error st err = 
  { iserror = true ;  error = err; result = Lst []; targetstr = st.targetstr; index = st.index }


let in_channel_to_bytes input =
  let len = in_channel_length input in  
  let barr = Bytes.create len in
  really_input input barr 0 len;
  barr



let bit n = fun st ->
  if st.iserror then st else
  if (st.index >= (Bytes.length st.targetstr)*8 ) then update_state_when_error st ("tried to match bit 0, but got unexcepted end of input.") 
  else  let pos = st.index mod 8 in
    let nth = st.index / 8 in
    let byte = Bytes.get_uint8 st.targetstr nth  in
    let num = (Int.shift_right_logical (Int.logand byte  (Int.shift_left 1 pos))  pos) in
    if (num = n) || (n = 2)  then  update_state st (Integer num)  (st.index+1)
    else  update_state_when_error st  ("tried to match " ^ (string_of_int n) ^ ", but got " ^ (string_of_int num) )

let bit_bigend n = fun st -> 
 if st.iserror then st else
  if (st.index >= (Bytes.length st.targetstr)*8 ) then update_state_when_error st ("tried to match bit 0, but got unexcepted end of input.") 
  else  let pos = 7 - (st.index mod 8) in
    let nth = st.index / 8 in
    let byte = Bytes.get_uint8 st.targetstr nth  in
    let num = (Int.shift_right_logical (Int.logand byte  (Int.shift_left 1 pos))  pos) in
    if (num = n) || (n = 2)  then  update_state st (Integer num)  (st.index+1)
    else  update_state_when_error st  ("tried to match " ^ (string_of_int n) ^ ", but got " ^ (string_of_int num) )


  
let strmatch s = fun st ->
  if st.iserror then st
  else if is_end st  then update_state_when_error st ("tried to match " ^ s ^ ", but got unexcepted end of input.") 
  else  match  (Str.string_match (Str.regexp s) st.targetstr st.index )  with
  | true -> update_state st (Str (Str.matched_string st.targetstr) )  (st.index + (String.length (Str.matched_string st.targetstr) ))
  | _ ->  update_state_when_error st  ("tried to match " ^ s  ^ ", but got " ^ (rest_input st) )


let ( <|> ) p q  = fun st ->
  if st.iserror then st
  else let newst = p st in
    match newst.iserror with
    | false -> newst
    | _ -> q st

let append_result_with_parser p oldst =
  let newst = p oldst  in
  if newst.iserror then newst else 
  {
    newst with result = ( match oldst.result with
            |Lst l ->  Lst (append_element newst.result l)
            | x ->  Lst [x;newst.result] )
  }
  
let seq parsers =
  let rec loop ps st  = match ( ps , st.iserror  )with 
    | ([],_)  -> st 
    | (_ , f) when f = true -> st 
    | (p::r , _) -> loop  r ( append_result_with_parser  p st)
  in
  fun st ->   if st.iserror then st else loop parsers {st with result = Lst []  } 



(** map *)
let ( ==> ) pr fn =
  fun st -> let nextst = pr st in
    if nextst.iserror then  nextst
    else update_state_result nextst (fn nextst.result)
        
(** error map *)
let ( ==>! ) pr fn =
  fun st -> let nextst = pr st in
    if not nextst.iserror then  nextst
    else update_state_when_error nextst (fn nextst.error nextst.index) 

(** chain *)
let ( >>> ) pr fn = fun st ->
  let nst = pr st in
  if nst.iserror then nst
  else (fn nst.result) nst

(** tag *)
let ( =>+ ) p  key =  p ==> (fun r  ->  Pair (key,r ) )

let remove_empty =  (fun r -> match r with | Lst l -> Lst (List.filter (fun e -> not (e = Lst []) ) l) | x -> x)

let chain fn = fun st -> append_result_with_parser (fn st.result) st 

let letters = strmatch "[a-zA-Z]+"  

let digits = strmatch "[0-9]+[.]?[0-9]*?" ==> (fun r -> match r  with
    | Str s -> if String.contains s '.' then Float (float_of_string s) else Integer (int_of_string s)
    |_ -> failwith "digits" )

let many p =
  let rec loop st = if is_end st then st
    else  match st.iserror with
  | true -> update_state st st.result st.index  
  | _ ->  loop  ( append_result_with_parser p st )
  in
  fun st -> if st.iserror then st else  loop st 
      
let many1 p =
  let rec loop st = if is_end st then st
    else match st.iserror with
  | true -> update_state st st.result st.index 
  | _ -> loop  (append_result_with_parser p st )
  in
  fun st ->
    if st.iserror then st 
    else
      let first = p st in
      match  first.iserror  with
      | true   ->  first
      | _ ->  loop first  

let rec remove_first_and_last lst : res  =  match lst with
  | Lst l  ->  List.nth l 1 
  | _  ->  Lst [] 
    
let between left right = fun mid ->
  seq [left; mid ;right]   ==> (remove_first_and_last)  ==> remove_empty 


let myparser  =  seq [ strmatch "hello"  ; strmatch "hello" ] 
                (* |=> result_map (fun res -> List.map String.uppercase_ascii) 
                   |=> error_map (fun msg i -> "meet error at index = " ^ string_of_int i )
                *)

let p2 =  (strmatch "h" <|> strmatch "j" )  >>>  (fun r ->  (if r = Str "h" then strmatch "1" else strmatch "2")
                                                            ==> (fun re -> match r with
                                                                | Str k ->  Pair (k,re)
                                                                | _ -> failwith "invalid_arg") =>+ "fuck" ) 
                                                 


let p = seq [letters ; strmatch ":" ; (letters <|> digits)]  (* |=> result_map (fun lst -> [List.nth lst 0 ; List.nth lst 2] ) *)
    
let between_backets = between (strmatch "(") (strmatch ")")
    
let  sepBy sep = fun p ->  fun st ->
  if st.iserror then st else
    let rec loop s res  =  match s.iserror with
      | true -> update_state s res  s.index 
      | _ ->  match (p s) with
        | newst  when  newst.iserror ->  update_state newst res newst.index 
        | newst -> 
          loop (sep newst)  ( match res with
            |Lst l ->  Lst (append_element newst.result l)
            | x ->  Lst [x;newst.result] )
    in
    loop st (Lst [])

let whites = strmatch "[ \t\r\n]*"

let ele = digits <|> letters
          
let arr =  between_backets ( sepBy (strmatch ",")  (ele)  )                                     

let rec nestarr st  = between_backets  ( sepBy (strmatch ",")  ( ele <|> nestarr )  ) st 

let run p targetstring =
  p {iserror = false ; error = "" ; result = Lst []  ;targetstr = targetstring ; index = 0} 


let  uint_of_bits ~is_bigend lst =
  let newlst = if is_bigend then List.rev lst else lst in
  let rec impl acc nth =
    if nth >= List.length newlst then acc 
    else impl ( acc + (Int.shift_left (List.nth newlst nth) nth)) ( nth + 1)      
  in
  impl 0 0 



let  uint_of_bits ~is_bigend lst =
  let newlst = if is_bigend then List.rev lst else lst in
  let rec impl acc nth =
    if nth >= List.length newlst then acc 
    else match  List.nth newlst nth with
      | Integer i ->  impl ( acc + (Int.shift_left i nth)) ( nth + 1)
      |_ -> failwith "the element of input list must be a bit "
  in
  impl 0 0


let int_of_bits ~is_bigend lst =
  let newlst = if is_bigend then lst else List.rev lst in
  let Integer sign = List.nth newlst 0 in
  let len =  List.length newlst in 
  let rec impl acc nth =
    if nth >= len  then if sign = 0 then acc else ( -1*acc -1)
    else  match List.nth newlst nth  with
      | Integer i -> if sign = 0 then impl (acc+(Int.shift_left i (len-1-nth))) (nth + 1) else impl (acc+(Int.shift_left (1-i) (len-1-nth)) ) (nth+1) 
      | _ -> raise (invalid_arg "the element must be a bit")
  in  impl 0 0
    



let uintn ~is_bigend n = seq ( List.init n (fun x -> bit 2) )  ==> (fun r -> match  r with
    | Lst l -> Integer (uint_of_bits ~is_bigend:is_bigend l ) 
    | _   -> failwith "only accept  a bit list "
  )


let intn ~is_bigend n = seq ( List.init n (fun x -> bit 2) )   ==>  (fun r -> match  r with
    | Lst l -> Integer (int_of_bits ~is_bigend:is_bigend l ) 
    | _   -> failwith "only accept  a bit list "
  )

;; 
(* ------------------------------------------------------------------------------------------------ *)
module Env  = Map.Make(String)  
let operators = strmatch "\\+" <|> strmatch "-" <|> strmatch "\\*" <|> strmatch "/" <|> strmatch "define" 

let space = strmatch "[ \t\n\r]" ==> (fun r -> Lst [])
let spaces = strmatch "[ \t\n\r]+" ==> (fun r -> Lst [])
let rec fn st =between_backets( seq[ strmatch "fn" ; spaces ; between_backets(letters); spaces ; operations   ]
                                ==> remove_empty ) st
and call st = between_backets(seq [ letters; spaces ;operations ] ==> remove_empty) st  
and operations st = ( letters <|> digits<|> fn <|> call <|> between_backets(seq [
    operators;
    spaces;
    operations;
    spaces;
    operations
  ] ==> remove_empty  )) st

let sexprs = many1 (operations) 

let extend_env  (id:res) (x:res)  (env:res Env.t ref)  = match (id , x) with
  | (Str name , num )  ->  env := (Env.add name num !env) 
  | _ -> failwith "(define name value)"

let deref name env = try Env.find name !env
  with
  | _ -> failwith ("not found: " ^ name)

let eval_helper opf a b  =   match (a ,  b) with
      | (Integer i,Integer j) ->  Integer (int_of_float (opf (float_of_int i)  (float_of_int j) ) )
      | (Integer i , Float f) -> Float ( opf (float_of_int i) f) 
      | (Float f, Integer i) -> Float ( opf f  (float_of_int i) )
      | (Float f , Float g) -> Float (opf f g)


let env0 = ref Env.empty

let rec eval expr ev  =
   match expr   with
      |Str id ->  deref id ev
      |Integer i -> Integer i 
      |Float f ->  Float f 
      |Lst l ->
        begin let a =   (List.nth l 1)  in
          let b = if List.length l > 2 then (List.nth l 2) else Lst [] in
          match (List.nth l 0) with
          |Str "fn" ->  Pair ((get_str a) , b) 
          |Str "define" ->  (extend_env a (eval b ev) ev); (Lst [])
          |Str "+" -> eval_helper ( +. ) (eval a ev) (eval b ev)
          |Str "-" -> eval_helper ( -. ) (eval a ev) (eval b ev)
          |Str "*" -> eval_helper ( *. ) (eval a ev) (eval b ev)
          |Str "/" -> eval_helper ( /. ) (eval a ev) (eval b ev)
          |Str id -> let p = deref id ev in
            let name = get_pair_fst p in 
            let body = get_pair_snd p in 
            let value = (eval a ev) in 
            let tmpenv = ref (Env.add name value !ev) in
            eval body tmpenv  
          | _ -> failwith ""
        end 
      | _ -> raise (invalid_arg "invalid expr")

  
let interp str =
 eval   (run operations str).result  env0 
        
        
