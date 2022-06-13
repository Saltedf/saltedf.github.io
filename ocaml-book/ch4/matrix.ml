let is_valid_matrix  = function
    |[] -> false
    |[[]] -> false 
    |r::rows -> let l = List.length r in
       List.fold_left (fun acc e ->  (l!=0) && (List.length e = l)  && acc)  true rows 
(*
let add_row_vectors v1 v2 =
  if List.length v1 != List.length v2 then failwith "two vectors must have same dim"
  else 
    let rec impl acc v1 v2 =
      match (v1,v2) with 
      | (h1::t1,h2::t2) -> impl ((h1 + h2)::acc) t1 t2
      | _ -> List.rev acc
    in  impl [] v1 v2
;;
*)
let fold_map  op init f lst1 lst2  =
    if List.length lst1 != List.length lst2 then raise ( Invalid_argument "two lists should have same length" )
    else
    let rec loop acc l1 l2 = match (l1,l2) with
      | (h1::t1, h2::t2) -> loop (op (f h1 h2) acc) t1 t2
      | _ -> acc
    in loop init lst1 lst2
;;

let map2 f l1 l2  =List.rev (fold_map (fun e acc -> e::acc) [] f l1 l2) ;;
      
let add_row_vectors = map2 ( + ) 

let matrix_add = map2 add_row_vectors
    
let dot_product_row_vectors = fold_map ( + ) 0 ( * ) ;;

let colu_vector_of_row_vector  = List.map (fun e -> [e] )
    
let cons_colu_and_row colu row =  map2 ( @ )  colu (colu_vector_of_row_vector row)
    
let matrix_transposition m =
  if not(is_valid_matrix m) then raise (Invalid_argument "the input matrix is invalid")
  else
    match m with
    | h::t -> List.fold_left  cons_colu_and_row  (colu_vector_of_row_vector h) t
    | _ -> raise (Invalid_argument "the input matrix is invalid") 
;;

let multiply_matrices m1 m2 =
  let n = (matrix_transposition m2) in
  let rec impl  acc m1 = 
    match m1 with
    |[] -> List.rev acc 
    |row::rest -> impl ((List.map  (fun x -> dot_product_row_vectors x row) n  )::acc) rest 
  in impl [] m1
;;
