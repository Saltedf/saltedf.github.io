let rec sum = function
  | [] -> 1 
  | h::t -> h + sum t  
