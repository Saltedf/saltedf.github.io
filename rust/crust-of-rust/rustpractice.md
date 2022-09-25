

```rust


// 修复下面代码的错误并尽可能少的修改
fn main() {
    let (mut x, y) = (1, 2);
    x += 2;

    assert_eq!(x, 3);
    assert_eq!(y, 2);
}



fn main() {
    let (x, y);
    (x,..) = (3, 4);
    [.., y] = [1, 2];
    // 填空，让代码工作
    assert_eq!([x,y], [3,2]);
} 


```



```rust
//  修改 `assert_eq!` 让代码工作
fn main() {
    let x = 5;
    assert_eq!("i32".to_string(), type_of(&x));
}

// 以下函数可以获取传入参数的类型，并返回类型的字符串形式，例如  "i8", "u8", "i32", "u32"
fn type_of<T>(_: &T) -> String {
    format!("{}", std::any::type_name::<T>())
}
```

```
// 解决代码中的错误和 `panic`
fn main() {
   let v1 = 251_u16 + 8;
   let v2 = i16::checked_add(251, 8).unwrap();
   println!("{},{}",v1,v2);
}
```

