open Stdlib

let descend lst =
  lst |> ( List.sort  Stdlib.compare )  |> List.rev
;;
