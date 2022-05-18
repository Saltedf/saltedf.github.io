type day = Mon | Tues | Wed | Thur | Fri | Sat | Sun

let nextday = function
  | Mon -> Tues
  | Tues -> Wed
  | Wed -> Thur
  | Thur -> Fri
  | Fri -> Sat
  | Sat -> Sun
  | Sun -> Mon 
  
