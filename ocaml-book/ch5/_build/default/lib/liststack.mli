
type 'a stack
exception StackIsEmpty
val empty : 'a stack
val is_empty : 'a stack -> bool
val push : 'a -> 'a stack -> 'a stack
val peek : 'a stack -> 'a
val pop : 'a stack -> 'a stack
val size : 'a stack -> int

