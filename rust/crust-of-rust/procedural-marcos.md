类函数宏:

``` rust
vec![1,3,5];
```

等价于:

``` rust
{
    let mut v = Vec::new();
    v.push(1);
    v.push(3);
    v.push(5);
    v
}
```

写成宏的形式就是:

``` rust
#[macro_export]
macro_rules! myvec {
    ($($e: expr),*) => (
    {
    let mut v = Vec::new();
    $(v.push($e);)*
    v
    }
    );
}
```

`($e:expr),*` 表示 由逗号分隔的表达式序列. `myvec![1,2,3]`

而 `($e:expr,)*` 则表示零个或多个表达式+逗号的序列. `myvec[1,2,3,]`

`drive macro`:

``` rust
#[derive(Serialize,Deserialize)]
struct Foo {
    bar : usize 
}
```

`attribute macro`:

``` rust
#[test]
fn mytest {
    //.....
}

#[route(get,"/")]
fn foo() {
    // ...
}
```

展开宏:

emacs + lsp-mode + rust-analyzer `M-x lsp-rust-analyzer-expand-macro`

实现derivie macro: `#[derive(Builder)]`

1.  proc-macro 要在一个单独的crate库中被创建

2.  要将此lib标记为 **过程宏**

``` toml
[lib]
proc-macro = true
```

1.  必要的依赖:

``` toml
[dependencies]
syn = {version = "0.15", features = ["extra-traits"] }  # 用于为DeriveInput(即ast)实现 Debug , 便于调试 
quote = "0.6"
```

1.  创建对应于 `#[derive(Builder)]` 的函数 :

``` rust
use proc_macro::TokenStream;
#[proc_marco_derive(Builder)]
pub fn derive(input : TokenStream) -> TokenStream {
    // ...
}
```

1.  用 `syn` 将 `token` 流转换为AST

``` rust
use syn::{parse_macro_input,DeriveInput};
// in fn body : 
parse_macro_input!(input as DeriveInput)
```

1.  用 `quote!` 指定要增加的代码模板对应的ast

``` rust
use quote::quote;
// in fn body :
let expanded = quote! {
    // ...  导出宏为struct/enum额外增加的代码模板 
};
```

1.  将新增代码的ast转为token流并返回

``` rust
expanded.into() 
```

lv4 :

std::error::Error 在生成的代码中要使用绝对路径(全限定)

.clone() -\> ok<sub>or</sub>(self, )?

lv 6 rust编译器在macro expansion已经彻底完成后进行(performs) name
resolution.

需要clone()的时候就用,不用过分担心.

.collect() 需要标注容器类型: Vec\<\_\> , 但可以用 \_ 来省略元素的类型 .

stringify!() 可以在quote!{} 中使用 , 可将 \#xxx 转换为字符串 .

concat!(,) 可实现拼接 .
