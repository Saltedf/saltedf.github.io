
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

let map2 op lst1 lst2 =
  if List.length lst1 != List.length lst2 then raise ( Invalid_argument "two lists should have same length" )
  else
    let rec loop acc l1 l2 = match (l1,l2) with
      | (h1::t1, h2::t2) -> loop ((op h1 h2)::acc) t1 t2
      | _ -> List.rev acc
    in loop [] lst1 lst2
;;
               
      
let add_row_vectors = map2 ( + ) ;;


