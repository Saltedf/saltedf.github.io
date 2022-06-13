module type RingWithoutOfInt = sig
  type t

  val zero : t

  val one : t

  val ( + ) : t -> t -> t

  val ( ~- ) : t -> t

  val ( * ) : t -> t -> t

  val to_string : t -> string

end

module AddOfInt (W: RingWithoutOfInt ) = struct
  include W 
  let of_int n =
    let rec loop acc = function
      |0 -> acc
      |num -> loop W. (one + acc ) (num-1)
    in loop W.zero n
end


module type Ring = sig
  include RingWithoutOfInt
      
   val of_int : int -> t    
end

module type Field = sig
  include Ring
      
  val ( / ) : t -> t -> t
end

module IntRingImpl  = AddOfInt( struct
  type t = int

  let zero = 0

  let one = 1

  let ( + ) = ( + )

  let ( ~- ) = ( ~- )

  let ( * ) = ( * )

  let to_string = string_of_int
    
end )
    

module IntRing : Ring = IntRingImpl 

module IntField : Field = struct
  include IntRingImpl
  let ( / )  =   ( / )
end

module FloatRingImpl  = AddOfInt (struct
  type t = float

  let zero = 0.

  let one = 1.

  let ( + ) = ( +. )

  let ( ~- ) = ( ~-. )

  let ( * ) = ( *. )

  let to_string = string_of_float
    
end) 

module FloatRing : Ring = FloatRingImpl 

module FloatField : Field = struct
  include FloatRingImpl
  let ( / ) = ( /. )
end

module ToRational (F:Field) : Field  =struct
  
  include AddOfInt(struct 
  type t = F.t * F.t
  let zero = (F.zero,F.zero)
  let one = (F.one ,F.one)
  let ( + ) ((a,b):t) ((c,d):t) =  F. ((a * d) + (c * b), b * d)
  let ( ~- ) ((a, b):t) = F. (-a, b)
  let ( * ) (a, b) (c, d) = F. (a * c, b * d)
  let to_string (a, b) = F.to_string a ^ "/" ^ F.to_string b 
end )
      
  let ( / ) ((a, b):t) ((c, d):t)  =F. (a * d, b * c)
end

module IntRational : Field  = ToRational(IntField)

module FloatRational : Field = ToRational(FloatField)
    


