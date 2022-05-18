open OUnit2

open Descend



let make_descend_testcase name expect lst =
  name >:: (fun _ -> assert_equal expect (descend lst) ) 
;;


let descend_test_suite = "test descend" >::: [
    make_descend_testcase "empty list" [] [] ;
    make_descend_testcase "one element" [3] [3] ;
    make_descend_testcase "ascending list" [3;2;1] [1;2;3] 

  ]

let _ = run_test_tt_main descend_test_suite



