# Ch1

## cargo创建并运行项目

`println!()` 是一个宏 `macro` , 它本质上是一段能生成代码的代码. 所有以
`!` 结尾的"函数"都是macro,

``` bash
mkdir -p parent/child # -p 选项能在创建child目录前先创建parent 
```

``` bash
cargo new 
```

不显示编译信息并运行

``` bash
cargo run --quiet
# Or: 
cargo run -q 
```

默认情况下cargo会创建一个debug版本的程序,

## 测试

新建目录tests

``` bash
$  tree -L 2
.
├── Cargo.lock
├── Cargo.toml
├── hello
│   └── src
├── src
│   ├── main
│   ├── main.rs
│   └── part2.rs
├── target
│   ├── CACHEDIR.TAG
│   ├── debug
│   ├── rls
│   └── tmp
└── tests
    └── cli.rs
```

``` rust
#[test]
fn works() {
    assert!(true);
}
```

``` rust
use std::process::Command;

#[test]
fn runs() {
    let mut cmd = Command::new("ls");
    let res = cmd.output(); // 返回类型为 Result 
    assert!(res.is_ok());
    assert!(false);
}
```

启动测试:

``` bash
cargo run # shell

M-x rust-test # emacs
```

只有环境变量中记录的命令才能直接运行:

查看环境变量, 并用 `tr` 将 `:` 替换为换行符

``` bash
echo $PATH | tr : '\n'
```

## 添加依赖

为了让我们自己写的程序能像命令一样用Command的方式调用, 我们需要一个包
`assert_cmd` ,因为它只是在测试中被使用,因此将它加入到
`[dev-dependencies]` 下:

``` toml
...
[dependencies]

[dev-dependencies]
assert_cmd = "1"
```

``` bash
cargo build
```

``` rust
use assert_cmd::Command; 

#[test]
fn runs() {
    let mut cmd = Command::cargo_bin("hellorust").unwrap();
    cmd.assert().success();
}
```

cargo<sub>bin创建一个运行hellorust程序的命令</sub>,
并返回一个Result类型的值, `unwrap()` 尝试将Result中Ok的内容取出来,
若不是Ok, 则会引发panic()

``` rust
pub enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

``` ocaml
(*OCaml*)
type ('t,'e) result =
    Ok of 't
  | Err of 'e
;;
```

## 退出码

命令行程序会返回一个退出码来说明程序运行结束的状态. 有一个命令 `true`
总是将退出码置为0

``` bash
true
echo $?
0
```

类似地, `false` 命令总是将退出码置为1

我们可以自己写一个 `true` 创建 `src/bin/true.rs`

``` rust
$ tree src/
src/
├── bin
│ └── true.rs
└── main.rs
```

``` rust
fn main() {
    std::process::exit(0);
}
```

``` bash
cargo run --quite --bin true
```

并对其进行测试:

``` rust
#[test]
fn true_ok() {
    let mut cmd = Command::cargo_bin("true").unwrap();
    cmd.assert().success();
}
```

注: rust的test不一定会按照顺序执行,
因为rust本身是一本并发安全的语言,它可以并行运行多个测试.

可以使它只用一个线程进行测试:

``` bash
cargo test --test-threads=1
```

rust中的程序默认以0作为退出码, 因此true.rs可以写成:

``` rust
fn main() {} 
```

同理编写 `false.rs` 并对其进行测试

``` rust
fn main(){
    std::process::exit(1);
}
```

也能用 `abort()` 实现退出码为1

``` rust
fn main (){
    std::process::abort();
}
```

``` rust
cargo run -q --bin false
```

``` rust
fn false_not_ok() {
    let mut cmd = Command::cargo_bin("false").unwrap();
    cmd.assert().failure();
  }
```

``` rust
cargo test 
```

退出码使得程序能够用 `&&` 组合起来, 当中间遇到退出码非0时,
后续的命令不会被执行. eg : `false && ls`

## 测试输出结果

假设要对 `src/main.rs` 的输出进行测试:

``` rust
fn main(){
    println!("hello");
}
```

``` rust
fn runs() {
    let mut cmd = Command::cargo_bin("hellorust").unwrap();
    cmd.assert().success().stdout("hello\n") ;
}
```

# Ch2 echo

## echo的行为

``` bash
echo hello
hello
```

``` bash
echo "hello world"
hello world
```

``` bash
echo hello   world # 传入了两个参数 
hello world
```

echo会在字符串末尾自动添加换行, 因此这里有两次换行

``` bash
echo "a\n" 
a

```

这里只有一次换行, 因为-n选项使得末尾换行被替换为 `'\c'`

``` bash
echo -n "a\n" 
a
```

``` bash
echo -n  "hello"
hello%
echo -n "a"  
a%            
```

## 获取命令行参数

``` rust
fn main() {
    println!("{:?}", std::env::args()); 
}
```

`{}` 是一个占位符, 只有实现了 `std::fmt:Display` 的对象才能用它打印.
在这里不能用, 而是要使用 `{:?}` 来输出 debug 版本的struct

``` bash
# inner: 后面的就是struct中的内容  
~/src/rust-learning/echor $ cargo run -q
Args { inner: ["target/debug/echor"] }
```

``` bash
$ cargo run -q arg1 hello

Args { inner: ["target/debug/echor", "arg1", "hello"] }
```

但是加入我们希望传入一个选项参数, `-n` 会被当成是cargo的参数

``` bash
cargo run -n hello
```

因此需要用 `--` 来指明cargo选项参数的结束:

``` bash
cargo run -- -n hello 
```

``` bash
$ cargo run -q -- -n -q hello
Args { inner: ["target/debug/echor", "-n", "-q", "hello"] }
```

## 用 `clap` 解析命令行参数

    [dependencies]
    clap = "2"

    cargo build

查看文件大小

``` bash
du -shc .
```

``` rust
use clap::App;

fn main() {
    let _matches = App::new("echor") // 应用名 
        .version("0.1.0")
        .author("sun")
        .about("echo in rust")
        .get_matches() ; // 解析命令行参数 
}

```

``` bash
$ cargo run -q -- -h
echor 0.1.0
sun
echo in rust

USAGE:
    echor

FLAGS:
    -h, --help       Prints help information
    -V, --version    Prints version information
```

``` rust
use clap::{App,Arg};


fn main() {

    //  println!("{:?}", std::env::args());
    let matches = App::new("echor") // 应用名 
    .version("0.1.0")
    .author("sun")
    .about("echo in rust")
    .arg(Arg::with_name("test") // 作为map的key, 用于取出值
         .value_name("TEXT") 
         .help("input test")
         .required(true) // 是否是必须的参数 
         .min_values(1), // 且此参数至少要有一个 
    )
    .arg(Arg::with_name("omit_newline") 
         .short("n")
         .help("don't print newline")
         .takes_value(false), // 无需为此选项传值 
    )
    .get_matches() ; // 解析命令行参数
    println!("{:#?}", matches); //用换行和缩进进行打印 
}
```

``` rust
 $ cargo run -q -- -n  hello world 
ArgMatches {
    args: {
        "omit_newline": MatchedArg {
            occurs: 1,
            indices: [
                1,
            ],
            vals: [],
        },
        "test": MatchedArg {
            occurs: 2,
            indices: [
                2,
                3,
            ],
            vals: [
                "hello",
                "world",
            ],
        },
    },
    subcommand: None,
    usage: Some(
        "USAGE:\n    echor [FLAGS] <TEXT>...",
    ),
}
```

``` bash
$ cargo run -q -- -h
echor 0.1.0
sun
echo in rust

USAGE:
    echor [FLAGS] <TEXT>...

FLAGS:
    -h, --help       Prints help information
    -n               don't print newline
    -V, --version    Prints version information

ARGS:
    <TEXT>...    input test
```

## 根据 `with_name()` 取出参数值

``` rust
ArgMatches::values_of -> Option<Values> // Values是迭代器 

ArgMatches::values_of_lossy -> Option<Vec<String>> 
```

取出必需的 "text" 参数 :

``` rust
matches.values_of_lossy("text").unwrap(); 
```

对可选的 `-n` 参数, 要先判断其是否存在

``` rust
matches.is_present("omit_newline");
```

为了让输出的结果h之间每个都恰好间隔以后一个空格, 我们需要用到
`Vec::join` 函数 :

``` rust
let v = vec!["hello","world"];
println!("{}", v.join("@")) ;
```

``` rust
hello@world
```

``` rust
use clap::{App,Arg};

fn main() {
    let matches = App::new("echor") // 应用名 
    .version("0.1.0")
    .author("sun")
    .about("echo in rust")
    .arg(Arg::with_name("test") // 作为map的key, 用于取出值
         .value_name("TEXT") 
         .help("input test")
         .required(true) // 是否是必须的参数 
         .min_values(1), // 且此参数至少要有一个 
    )
    .arg(Arg::with_name("omit_newline") 
         .short("n")
         .help("don't print newline")
         .takes_value(false), // 无需为此选项传值 
    )
    .get_matches() ; // 解析命令行参数

    let text = matches.values_of_lossy("text").unwrap();
    let is_newline = matches.is_present("omit_newline");

    print!("{}{}", text.join(" "), if is_newline  {""} else {"\n" }) ;
}
```

## 编写集成测试

为了进行测试, 除了使用 `assert_cmd` 之外, 还要使用 `predicates` , 即:
"谓词".

``` toml
[dev-dependencies]
 assert_cmd = "2"
 predicates = "2"
```

因为有的时候测试应满足的条件不是简单地判断是否等于某个值,
比如说输出中应包含了 "USAGE" 这个字符串. 这时候就需要使用"谓词".

``` rust
use assert_cmd::Command;
use predicates::prelude::* ;
#[test]
fn dies_no_args() {
    let mut cmd = Command::cargo_bin("echor").unwrap();
    cmd.assert().failure().stderr(predicate::str::contains("USAGE") ); 
}
```

另外有一个技巧就是为一组测试的函数名用相同的前缀, 例如 `dies`
这样可以使cargo test只运行这些包含了前缀的测试:

    cargo test dies

用 `.arg()` 传入参数进行测试:

``` rust
#[test]
fn one_arg(){
    let mut cmd = Command::cargo_bin("echor").unwrap();
    cmd.arg("hello").assert().success().stdout(predicate::str::contains("hello"));
}
```

### 和echo的输出进行对比

首先要生成echo的结果:

``` bash
#!/bin/bash

OUTDIR="tests/expected"
# 注意中括号之间的空格 
[[ ! -d "$OUTDIR" ]] && mkdir -p "$OUTDIR" # 判断是否存在此目录, 不存在则创建 

echo "hello there" > $OUTDIR/hello1
echo "hello"   "there" > $OUTDIR/hello2
echo -n "hello   there" > $OUTDIR/hello1n
echo -n "hello" "there" > $OUTDIR/hello2n
```

然后分别编写测试

``` rust
use std::fs;
#[test]
fn hello1(){
    let outfile = "tests/expected/hello1" ;
    let expected = fs::read_to_string(outfile).unwrap();
    let mut cmd = Command::cargo_bin("echor").unwrap();
    cmd.arg("hello there").assert().success().stdout(expected);
}
```

在上面的所有代码中, 我们都直接使用了 `unwrap()` 来取出Result中的OK值,
但这也默认了程序的结果始终都是正常的. 这样的假设当然是不合理的,
因此我们要创建一个Result类型:

``` rust
//  TestResult = Ok of unit | Err of Box<dyn std::error::Error>
type TestResult = Result<(), Box<dyn std::error::Error>> ;
```

- `()` 表示 `Ok` 是 `unit` 类型
- `Box` 表示这是一个指向堆中内存的指针
- `dyn` 表示对 `std::error::Error` 进行的方法调用是动态分发的(多态)

之前所有的测试函数的返回值都是 `unit` 类型, 现在用 `TestResult`
来取代它. 之前用 `unwrap()` 来对 `Ok` 值进行解包, 并当遇到 `Err`
类型时触发 `panic` 使程序挂掉. 现在除了用 `TestResult` 作为返回类型,
还用 `?` 来取代 `unwrap` ? 同样是匹配 `Ok` / `Err` 的语法糖, 当为 `Ok`
时, 将其中的值取出来, 当为 `Err` 时, 会提前 `return Err<XX>`,
其中的类型是函数的返回类型决定的: `->Result<OO,XX>`. 这点和 `unwrap()`
不同的, 不会直接触发 panic

# Ch3 cat

# Ch4 head

# Ch5 wc

# Ch6 uniq

# Ch7 find

# Ch8 cut

# Ch9 grep

# Ch10 comm

# Ch11 tail

# Ch12 fortune

# Ch13 cal

# Ch14 ls
