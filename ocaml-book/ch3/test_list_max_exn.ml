open OUnit2

let rec list_max = function 
  | [x] -> x 
  | h::t -> max h (list_max t) 
  | _ -> failwith "list_max"
;;


let test_list_max = "list_max" >::: [
    "empty list" >:: (fun _ -> assert_raises (Failure "list_max") (fun () -> list_max []) ) ;
    "nonempty list" >:: (fun _ -> assert_equal 3 (list_max [1;2;3;1] )) 
  ]

let _ = run_test_tt_main test_list_max ;;

