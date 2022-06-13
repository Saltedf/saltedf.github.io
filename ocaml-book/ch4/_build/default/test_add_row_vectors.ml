open OUnit2
open Stdlib
open Matrix
    


let make_test_equal name  expected v1 v2 =
  name >:: (fun _ -> assert_equal expected  (add_row_vectors v1 v2) )

let make_test_raise name  v1 v2 =
  name >:: (fun _ -> assert_raises (Invalid_argument "two lists should have same length") (fun _ -> add_row_vectors v1 v2) ) 
  

let test_add_row_vectors = "add_row_vectors" >:::[
    make_test_equal "empty vectors" [] [] [] ;
    make_test_raise "different length" [2;4] [2;4;5];
    make_test_equal "add 3-dim vectors" [4;4;4]  [1;2;3] [3;2;1] ; 
  ]


let _ = run_test_tt_main test_add_row_vectors 
