open OUnit2
open Sum

let make_testcase_for_sum  name expected  lst  =
   name >:: (fun _ -> assert_equal expected (sum lst) ~printer:string_of_int )




(* let tests = "test suite for sum" >::: [
 *     "empty" >:: (fun _ -> assert_equal 0 (sum []) ~printer:string_of_int  ) ;
 *     "singleton" >:: (fun _ -> assert_equal 1 (sum [1]) ~printer:string_of_int ) ;
 *     "two elements" >:: (fun _ -> assert_equal 3 (sum [1;2]) ~printer:string_of_int );
 *   ] *)
 


let better_tests = "better test suite for sum" >::: [
      make_testcase_for_sum "empty"  0 [] ;
      make_testcase_for_sum "singleton" 1 [1] ;
      make_testcase_for_sum "two elements" 3 [1;2] ;
    ]


let _ = run_test_tt_main better_tests 

