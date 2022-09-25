# 动态dyn分发





忘记在哪看到的这个例子了. 我汉化了一下, 并为汇编代码加了详细注释.

```rust
trait GetInt {
    fn get_int(&self) -> u64;
}

struct WhyNotU8 {// vtable stored at section L__unnamed_1
    x: u8
}

struct ActualU64 {// vtable stored at section L__unnamed_2
    x: u64
}

impl GetInt for WhyNotU8 {
    fn get_int(&self) -> u64 {
        self.x as u64
    } 
} 

impl GetInt for ActualU64 {
    fn get_int(&self) -> u64 {
        self.x
    }
}


// `&dyn`表明我们要使用动态分发,而不是单态化. 因此在生成的汇编中只有一个`retrieve_int`函数.
// 若此处使用泛型,那么在生成的汇编中,对每个实现GetInt的类型都有一个相应的`retrieve_int`函数 
pub fn retrieve_int(u: &dyn GetInt) { // <<<<<<<<<<<<<<<<!!!!!!!!!!!!!!!!
   
  	// 在汇编中, 我们仅仅调用传入rsi中的地址(对应get_int的地址)
    //并期望在调用即将发生前, rsi被正确设置
    let x = u.get_int();
}

pub fn do_call() {
   
  // 即便 `WhyNotU8` 和 `ActualU64` 对应的vtable表项中有 `core::ptr::real_drop_in_place`的函数指针, 这个函数也从来不被实际调用. 
    let a = WhyNotU8 { x: 0 };
    let b = ActualU64 { x: 0 };

    retrieve_int(&a);
    retrieve_int(&b);
}
```



汇编: `-C opt-level=0`

```gas
core::ptr::drop_in_place<example::WhyNotU8>: 
  retq 

core::ptr::drop_in_place<example::ActualU64>: 
  retq 

<example::WhyNotU8 as example::GetInt>::get_int: 
  movzbl (%rdi), %eax  # 将get_int的第1参数(引用/指针)所指向的数据 放入eax作为返回值 
  retq 

<example::ActualU64 as example::GetInt>::get_int: 
  movq (%rdi), %rax  # 将get_int的第1参数(引用/指针)所指向的数据 放入rax作为返回值 
  retq 

example::retrieve_int:     # fn retrieve_int(u: &dyn GetInt) -> ()
  pushq %rax      # 为了满足规定:call之前stack是按16字节对齐的(上一次call压入的8字节返回地址破坏了这点)
  callq *24(%rsi)  # rsi 为每个Table表项的起始地址
  		           # rsi + 24处存放着指向 函数<example::??? as example::GetInt>::get_int 的指针 
 			   # call *24(%rsi) = call *(rsi+24) ==> 调用对应的get_int()函数 	
  popq %rax  
  retq

example::do_call: 
  subq $24, %rsp  	#在stack上分配 24 字节 
  movb $0, 15(%rsp) 	# let b = ActualU64 { x: 0 };
  movq $0, 16(%rsp) 	# let a = WhyNotU8 { x: 0 };
  leaq 15(%rsp), %rdi 	# rdi <- rsp + 15  将对b的引用作为第一参数
  leaq .L__unnamed_1(%rip), %rsi 		# rsi <- 表项.L__unnamed_1的起始地址
  callq *example::retrieve_int@GOTPCREL(%rip)  	# 调用 retrieve_int()
  leaq 16(%rsp), %rdi 		# rdi <- rsp + 16  将对a的引用作为第一参数
  leaq .L__unnamed_2(%rip), %rsi 		# rsi <- 表项.L__unnamed_2的起始地址
  callq *example::retrieve_int@GOTPCREL(%rip)		#调用 retrieve_int()
  addq $24, %rsp 	  # 归还 stack 上空间
  retq 


#  vtable: 
.L__unnamed_1: # 此处地址 + 24 字节 == 指向get_int()的指针 
  .quad core::ptr::drop_in_place<example::WhyNotU8> # 8 字节 
  .asciz "\001\000\000\000\000\000\000\000\001\000\000\000\000\000\000" # 16 = 15 + 1 字节
  .quad <example::WhyNotU8 as example::GetInt>::get_int # 8 字节, 指向相应的get_int()的指针 


.L__unnamed_2: # 此处地址 + 24 字节 == 指向get_int()的指针 
  .quad core::ptr::drop_in_place<example::ActualU64>  # 8 字节  
  .asciz "\b\000\000\000\000\000\000\000\b\000\000\000\000\000\000" # 16 = 15 + 1 字节
  .quad <example::ActualU64 as example::GetInt>::get_int  # 8 字节,  指向相应的get_int()的指针 
```



更进一步, 改写为静态分派做对比:
能发现上面采用动态分派时只生成了一个`retrieve_int()` . 而改成静态分派后分别对于两个类型 (`WhyNotU8`, `ActualU64`) 都生成了相应的 `retrieve_int_static()` , 并且没有产生 `vtable` .

```rust
// ... 省略相同代码 ... 
fn retrieve_int_static(u:&impl GetInt){
     let x = u.get_int();
}

pub fn do_call() {
   
    let a = WhyNotU8 { x: 0 };
    let b = ActualU64 { x: 0 };

    retrieve_int_static(&a);
    retrieve_int_static(&b);
}
```



对应汇编:

```gas
<example::WhyNotU8 as example::GetInt>::get_int:
        movzbl  (%rdi), %eax
        retq

<example::ActualU64 as example::GetInt>::get_int:
        movq    (%rdi), %rax
        retq

example::retrieve_int_static:  # 编译时为WhyNotU8生成的retrieve_int_static
        pushq   %rax
        callq   *<example::WhyNotU8 as example::GetInt>::get_int@GOTPCREL(%rip)
        popq    %rax
        retq

example::retrieve_int_static:  # 编译时为ActualU64生成的retrieve_int_static
        pushq   %rax
        callq   *<example::ActualU64 as example::GetInt>::get_int@GOTPCREL(%rip)
        popq    %rax
        retq

example::do_call:
        subq    $24, %rsp
        movb    $0, 15(%rsp)
        movq    $0, 16(%rsp)
        leaq    15(%rsp), %rdi
        callq   example::retrieve_int_static
        leaq    16(%rsp), %rdi
        callq   example::retrieve_int_static
        addq    $24, %rsp
        retq
```



https://stackoverflow.com/questions/37773787/why-does-this-function-push-rax-to-the-stack-as-the-first-operation

https://oswalt.dev/2021/06/polymorphism-in-rust/


> 关于call之前用push reg进行栈对齐的补充: 
>
>假如把上面这个函数改成有返回值的: 
>
>```rust
>pub fn retrieve_int(u: &dyn GetInt)->u64 {
>```
>
>
>
>```gas
>example::retrieve_int:
>   pushq   %rax
>   callq   *24(%rsi)
>   movq    %rax, (%rsp)
>   movq    (%rsp), %rax ;; 设置了返回值rax
>   popq    %rcx 
>   ;; !!不能再是popq %rax了,会破坏返回值!! 
>   ;; 为了抵消对齐用的push %rax, 应popq到一个当前无用的寄存器rcx
>   retq
>```
>
>
