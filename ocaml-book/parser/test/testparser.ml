open OUnit2



let test_dismatched reg s =
  (fun _ -> assert_raises (Parser.Dismatch ("tried to match " ^ reg ^ ", but got " ^ s) )  (fun () -> Parser.strmatch reg s ) )

let tests  = "parser tests" >::: [
    "string matched" >:: (fun _ -> assert_equal "Ok"  ( Parser.strmatch "hello" "helloworld"  ) ) ;
    
    "string dismatched"  >:: test_dismatched "hell" "firsthello" ; 
  ]


let _ = run_test_tt_main tests





