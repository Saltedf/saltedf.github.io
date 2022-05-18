open Fifth

open OUnit2

let make_fifth_testcase name expect lst =
  name >:: (fun _ -> assert_equal  expect (fifth lst) )
;;

let fifth_test = "test suite of fifth" >::: [
    make_fifth_testcase "empty list" 0 [] ;
    make_fifth_testcase "lewer than five elements" 0 [1;3;4;5] ;
    make_fifth_testcase "exactly five elements" 5 [1;2;3;4;5] ;
    make_fifth_testcase "more then five elements" 5 [1;2;3;4;5;6] 
  ]


let _  = run_test_tt_main fifth_test 
