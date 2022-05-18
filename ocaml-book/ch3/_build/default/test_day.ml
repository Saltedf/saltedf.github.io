open Day
open OUnit2



let make_nextday_testcase name expected d =
  name >:: (fun _ ->  assert_equal expected (nextday d ) )

let nextday_tests = "test suite for nextday " >::: [
    make_nextday_testcase "1" Tues  Mon ;
    make_nextday_testcase "2" Wed Tues ;
    make_nextday_testcase "3" Thur Wed ;
    make_nextday_testcase "4" Fri Thur ;
    make_nextday_testcase "5" Sat Fri ;
    make_nextday_testcase "6" Sun Sat ;
    make_nextday_testcase "7" Mon Sun ;
  ]




let _ = run_test_tt_main nextday_tests 





