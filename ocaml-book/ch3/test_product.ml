open OUnit2

open Product


let test_product = "test_product" >::: [

    "empty list" >:: (fun _ -> assert_equal 1 (product []) ) ;
    "one element" >:: (fun _ -> assert_equal 4 (product [4]) );
    "two elelemts" >:: (fun _ -> assert_equal 30 (product [5;6]) ) ;
    "contains zero" >:: (fun _ -> assert_equal 0 (product [0;34;54;12;1;3;5;6;] )  );
    

  ]



let _ = run_test_tt_main test_product


