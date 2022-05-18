


  let product lst =
    let rec product_tr acc = function 
      | [] -> acc 
      | h::t when h!=0 -> product_tr (h*acc) t
      | _ -> 0 
    in
    product_tr 1 lst



