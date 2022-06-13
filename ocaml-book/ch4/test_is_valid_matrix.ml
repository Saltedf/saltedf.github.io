open OUnit2
open Stdlib
open Matrix
    

let make_test_case  name expected matrix =
  name >:: (fun _ -> assert_equal expected (is_valid_matrix matrix) )  

let test_suites = "is_valid_matrix" >::: [
    make_test_case "empty list" false [] ;
    make_test_case "empty int list" false [[]] ;
    make_test_case "more empty row vectors" false [[];[];[]];
    make_test_case "1-dim row vectors"  true  [[1];[2];[23]] ;
    make_test_case "row counts != colument counts"  false [[2];[23;4];[2;4]];
    make_test_case "3*3 matrix" true [[1;2;4];[3;4;5];[4;5;6]] ;
  ] 




let _ = run_test_tt_main test_suites  
