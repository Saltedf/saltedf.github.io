open OUnit2
open Stdlib   


   
let raise_expection () =
  raise (Failure "mytest")
;;
   


let mytests = "test suite" >::: [
    "test-raise-exceptions" >:: (fun _ -> assert_raises
				    (Failure "mytest") (fun () -> raise_expection ( ) ))
  ]


let _ = run_test_tt_main mytests ;; 



