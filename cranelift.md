//#+startup: content

# 数据结构

entity : Map/Set/List

bforest : 树

# 主要模块

`src` : clif-util.rs 中有 `main()` 函数

reader : 读取clif文件(文本格式IR),用来做测试

frontend : 生成IR

interpreter : IR解释器

preopt : 对IR的早期优化.

module : 链接?

codegen : IR -\> 可执行机器码

native : 检测host机器的架构.

object : 生成.o文件

# 不是必要的/暂时可不看的 模块:

jit : 实验性

umbrella : 无实际代码

serde : IR转JSON

isle : 生成rust代码的DSL (用于后端)

fuzzgen : 生成随机的 Cranelift modules

wasm

# frontend

创建IR形式的函数, 并用指令将其填充.

要先创建 FunctionBuilderContext. 并将其作为一个参数传给 FunctionBuilder

可变变量和IR value

1.  声明签名,并指定所使用的调用约定.
2.  为sig声明参数和返回值类型.
3.  创建一个FunctionBuilderContext 对象
4.  使用函数名和签名创建一个Function对象.
5.  用函数对象和函数builder上下文创建一个FunctionBuilder
6.  builder.create<sub>block</sub>()创建入口块
7.  

## EntryIndex

EntryIndex 的作用是为每个基本块生成一个唯一的标识符，方便在 Cranelift
内部进行引用和操作。可以通过 FunctionBuilder::create<sub>block</sub>()
方法创建一个新的基本块，并得到该基本块的
EntryIndex。在生成跳转指令时，可以通过 Switch::set<sub>entry</sub>()
方法为一个 Switch 表格添加新的条目，其中每个条目都是一个基本块的
EntryIndex 和一个对应的标签（通常是一个整数）组成的元组。

## switch.rs

测试emit()用: setup, 返回一个函数 接收两个参数: 第一个是default,
第二个是一个各个分支的值list

``` rust
let func : String = setup!(0, [0,]);
```

``` rust
macro_rules! setup {
   ($default:expr, [$($index:expr,)*]) => {{
       let mut func = Function::new();
       let mut func_ctx = FunctionBuilderContext::new();
       {
       let mut bx = FunctionBuilder::new(&mut func, &mut func_ctx);
       let block = bx.create_block();
       bx.switch_to_block(block);// 使得焦点移到block上, 从而能在block中填入指令/对基本块进行其他操作
       let val = bx.ins().iconst(types::I8, 0);//创建一条指令, 声明一个i8类型的值,用该值来决定应该跳往switch的哪个分支
       let mut switch = Switch::new();
       $(
           let block = bx.create_block(); //为每个输入list中的索引创建一个对应的空块 
           switch.set_entry($index, block);//
       )*
       switch.emit(&mut bx, val, Block::with_number($default).unwrap());
       //为函数生成分支代码
       }
       func
       .to_string()
       .trim_start_matches("function u0:0() fast {\n")
       .trim_end_matches("\n}\n")
       .to_string()
       // 将函数转为字符串形式, 并去掉头尾.
   }};
   }
```

分支:

``` rust
#[derive(Debug, Default)]
pub struct Switch {
    cases: HashMap<EntryIndex, Block>,
}
```

可见核心逻辑在 Switch.emit() 中.
switch结构本身只是用来生成分支指令的脚手架.

先来看emit的签名:

bx代表函数. val代表跳转基于的值.
otherwise表示default块(即各个分支都落空后,要前往的块)

``` rust
pub fn emit(self, bx: &mut FunctionBuilder, val: Value, otherwise: Block) 
```

我们用这个测试用例来研究emit的逻辑:

``` rust
#[test]
fn switch_many() {
    let func = setup!(0, [0, 1, 5, 7, 10, 11, 12,]);

    assert_eq!(
    func,

    "    jt0 = jump_table [block1, block2]
    jt1 = jump_table [block5, block6, block7]

block0:
    v0 = iconst.i8 0
    v1 = icmp_imm uge v0, 7  ; v0 = 0
    brnz v1, block9
    jump block8

block9:
    v2 = icmp_imm.i8 uge v0, 10  ; v0 = 0
    brnz v2, block10
    jump block11

block11:
    v3 = icmp_imm.i8 eq v0, 7  ; v0 = 0
    brnz v3, block4
    jump block0

block8:
    v4 = icmp_imm.i8 eq v0, 5  ; v0 = 0
    brnz v4, block3
    jump block12

block12:
    v5 = uextend.i32 v0  ; v0 = 0
    br_table v5, block0, jt0

block10:
    v6 = iadd_imm.i8 v0, -10  ; v0 = 0
    v7 = uextend.i32 v6
    br_table v7, block0, jt1"
    );
}
```

首先的几行是判断条件分支中的最大值是否超过了val的type所能表示的范围.若超过了则报错.
这段暂时不用深究.

``` rust
/// emit()
let max = self.cases.keys().max().copied().unwrap_or(0);
let val_ty = bx.func.dfg.value_type(val);
let val_ty_max = val_ty.bounds(false).1;
if max > val_ty_max {
    panic!(
    "The index type {} does not fit the maximum switch entry of {}",
    val_ty, max
    );
}
// ...
```

然后一行是: 从switch中计算出 ContiguousCaseRange (连续case范围) 的list

gpt:

collect<sub>contiguouscaseranges</sub> 方法用于收集所有连续的 case
range，并将它们组合成一个 Vec，以便后续处理。

在 build<sub>searchtree</sub> 方法中，首先通过
collect<sub>contiguouscaseranges</sub> 方法获取到所有连续的 case
range，接着通过递归的方式，将这些连续的 case range 分解成更小的 case
range。最终，每个 case range
都被组织成一个搜索树。这个搜索树是一个嵌套的结构，每个节点包含一个 case
和一个子搜索树。

在 build<sub>jumptables</sub>
方法中，根据搜索树，生成一个跳转表。跳转表的长度是 case range
的数量，每个 entry 是一个基本块。跳转表可以用于实现跳转语义，比如在
switch 表达式中跳转到对应的基本块。

总体来说，collect<sub>contiguouscaseranges</sub>
方法是用于帮助收集连续的 case
range，方便后续的处理。通过递归的方式，将搜索树分解成一个个小的 case
range，最终生成一个跳转表，实现了 switch 语义。

``` rust
/// emit() 
let contiguous_case_ranges = self.collect_contiguous_case_ranges();
```

我们抄一个测试来输出它:

``` rust
macro_rules! gen_switch {
    ($default:expr, [$($index:expr,)*]) => {{
    let mut func = Function::new();
    let mut func_ctx = FunctionBuilderContext::new();

    let mut bx = FunctionBuilder::new(&mut func, &mut func_ctx);
    let block = bx.create_block();
    bx.switch_to_block(block);
    let val = bx.ins().iconst(types::I8, 0);
    let mut switch = Switch::new();
    $(
        let block = bx.create_block();
        switch.set_entry($index, block);
    )*
        switch
    }};
}

#[test]
fn learn_collect_contiguous_case_ranges() {
    let switch = gen_switch!(0, [0, 1, 5, 7, 10, 11, 12,]);
    eprintln!("{:?}", switch.collect_contiguous_case_ranges());
}
```

输出如下,
可见此函数就是将连续的case值放在一组,并记录下这组中的最小case值.

``` rust
[
    ContiguousCaseRange {
        first_index: 0,
        blocks: [
            block1, // 0
            block2, // 1
        ],
    },
    ContiguousCaseRange {
        first_index: 5,
        blocks: [
            block3, // 5
        ],
    },
    ContiguousCaseRange {
        first_index: 7,
        blocks: [
            block4, // 7
        ],
    },
    ContiguousCaseRange {
        first_index: 10,
        blocks: [
            block5, // 10
            block6, // 11
            block7, // 12
        ],
    },
]
```

emit()的最后两行调用了switch的两个函数:

``` rust
let cases_and_jt_blocks =
    Self::build_search_tree(bx, val, otherwise, contiguous_case_ranges);

Self::build_jump_tables(bx, val, otherwise, cases_and_jt_blocks);
/// emit() 结束  
```

### `build_search_tree` ()

gpt: 在 switch.emit 中，搜索树（search
tree）是一个用于优化分支跳转的数据结构。其目的是在多个条件分支中，使用二分查找的方式快速定位到一个具体的分支。

在这里，搜索树被用来优化 switch 语句。switch 语句中的每个 case
都对应着一个基本块，但是如果 case
的数量过多，直接使用分支跳转的方式会带来较大的开销。因此，通过将 case
按照顺序分成多个连续的范围，并将每个范围中的最小值与最大值记录在搜索树的节点上，可以加速查找特定值的
case 所对应的基本块。通过这种方式，即使 switch 语句中的 case
数量很多，查找特定值对应的 case 所对应的基本块的开销也可以降到对数级别。

GPT:

``` rust
build_search_tree 方法是 SwitchBuilder 中的一个私有方法，其主要作用是构建搜索树。这个搜索树是一个二叉树，其中每个叶子节点对应于一个连续的 case 范围。每个非叶子节点表示对子树中所有 case 范围的分割。

方法的第一个参数是 bx: &mut FunctionBuilder，代表当前函数的生成器，第二个参数是 val: Value，代表 switch 表达式的值，第三个参数是 otherwise: Block，代表 switch 中的 otherwise 分支。方法的最后一个参数是一个 Vec<ContiguousCaseRange>，代表 switch 中所有连续的 case 范围。

在方法的第一行，我们创建了一个空的向量 cases_and_jt_blocks，用于存储最终生成的代码块和 jump table。

如果 contiguous_case_ranges 中的 case 数量小于等于 3，我们直接调用 build_search_branches 方法生成代码。build_search_branches 方法会生成一组比较，以及对应的分支代码，来处理每个 case 范围。

如果 contiguous_case_ranges 中的 case 数量大于 3，我们将 case 范围分成两部分，分别处理左右子树。具体地，我们通过 contiguous_case_ranges.len() / 2 来确定中间点，将左边的 case 范围放到 left 中，将右边的 case 范围放到 right 中。然后我们创建两个新的代码块 left_block 和 right_block，用于表示左子树和右子树。

接着，我们将 right[0].first_index 存储到 first_index 中，该值是右子树中第一个 case 的起始值。然后我们创建一个比较指令 should_take_right_side，用于比较 val 和 first_index 的大小。如果 val 大于或等于 first_index，则跳转到右子树；否则，跳转到左子树。

最后，我们使用 bx.seal_block 将新建的代码块封闭，表示我们已经完成了对该块的所有代码生成操作。最后，我们将左右子树压入堆栈，进行下一轮处理。如果堆栈为空，则所有子树已经处理完毕，我们返回 cases_and_jt_blocks。

该方法主要的目的是将 switch 中的 case 范围拆分成更小的块，以便更高效地生成代码。这个方法通过构建一个二叉树，将 case 范围按照值的范围进行分割，使得在代码生成时可以更快地找到需要跳转到哪个代码块。
```

先看 `build_search_tree`, 它以分好组的块作为输入.返回类型为:

``` rust
-> Vec<(EntryIndex, Block, Vec<Block>)>
```

这个结构将来用于生成 jt<sub>table</sub>

当连续case值形成的分组不超过3时,形成的块的数量较少,可以直接生成跳转代码,
用build<sub>searchbranches来实现此函数</sub>.

``` rust
let mut cases_and_jt_blocks = Vec::new(); //将作为输出结果

// Avoid allocation in the common case
if contiguous_case_ranges.len() <= 3 {
    Self::build_search_branches(
    bx,
    val,
    otherwise,
    contiguous_case_ranges,
    &mut cases_and_jt_blocks,
    );
    return cases_and_jt_blocks;
}
```

1.  `build_search_branches` ()

    首先是 声明了flag表明当前是否处在分支位置.

    ``` rust
    let mut was_branch = false;
    ```

    然后是一个辅助函数, 当处于分支位置时就执行,否则什么都不做.

    ``` rust
    let ins_fallthrough_jump = |was_branch: bool, bx: &mut FunctionBuilder| {
        if was_branch {
        let block = bx.create_block(); //创建一个新的基本块
        bx.ins().jump(block, &[]);//在目前所在分支块中插入一条jump, 用来跳转到新块
        bx.seal_block(block); // 为新块 "封口" (已处理好该块所有直接前驱)
        bx.switch_to_block(block); // 切换到这个新的空块中.
        }
    };
    ```

    ``` rust
    for ContiguousCaseRange { first_index, blocks, }
    in contiguous_case_ranges.into_iter().rev()
    //...
    ```

    反向遍历连续case值的分组, 举个例子就是:

    ``` rust
    let switch = gen_switch!(0, [0, 1, 5, 7, 8,]);
    ```

    ``` rust
    [
        ContiguousCaseRange { // 第三轮
        first_index: 0,
        blocks: [
            block1, // 0
            block2, // 1
        ],
        },
        ContiguousCaseRange { // 第二轮
        first_index: 5,
        blocks: [
            block3, // 5
        ],
        },
        ContiguousCaseRange { // 第一轮
        first_index: 7,
        blocks: [
            block4, // 7
            block5, // 8
        ],
        },
    ]
    ```

    循环内的具体逻辑是根据每个组中的长度以及最小值做判断,
    特殊处理长度=1或最小值=0的情况:

    ``` rust
    match (blocks.len(), first_index) {
        (1, 0) => {/** ... */}
        (1, _) => {/** ... */}
        (_, 0) => {/** ... */}
        (_, _) => {/** ... */}
    }
    was_branch = true;
    ```

    当组中只有一个块且case值为0时:

    ``` rust
    (1, 0) => {
        ins_fallthrough_jump(was_branch, bx); // 若处在分支位置, 则将下面的代码放到新块
        bx.ins().brz(val, blocks[0], &[]); // 根据val是否为0来判断是否跳转到这个分支
    }
    ```

    当组中只有一个case分支,且其case值不等于零时

    ``` rust
    (1, _) => {
        ins_fallthrough_jump(was_branch, bx); // 若处在分支位置, 则将下面的代码放到新块
        let is_good_val = icmp_imm_u128(bx, IntCC::Equal, val, first_index);
        // is_good_val = (val == 此分支的case值)
        bx.ins().brnz(is_good_val, blocks[0], &[]); // brnz为true时跳转
    }
    ```

    当组中的首个case值==0,且组中不止一个分支时,
    说明该组是switch的最后一部分,执行到这里时应该与之前的各组都不能匹配,而因为val\>=0
    , 因此最终只能跳入到这一部分.无需再生成jump otherwise.

    ``` rust
    (_, 0) => {
        // if `first_index` is 0, then `icmp_imm uge val, first_index` is trivially true
        let jt_block = bx.create_block();//创建一个空块,>= first_index时才跳入它
        bx.ins().jump(jt_block, &[]); //在当前块中插入一条jump, 跳到这个空块中
        bx.seal_block(jt_block); // 将这个空块封口
        cases_and_jt_blocks.push((first_index, jt_block, blocks));
        // `jump otherwise` below must not be hit, because the current block has been
        // filled above. This is the last iteration anyway, as 0 is the smallest
        // unsigned int, so just return here.
        return;
    }
    ```

    当连续case分支不止一个且最小case值不是零时:

    ``` rust
    (_, _) => {
        ins_fallthrough_jump(was_branch, bx);// 若为分支处,
        let jt_block = bx.create_block();// 创建空块, >=first_index时才跳入此块
        let is_good_val = // val >= first_index ? 
        icmp_imm_u128(bx, IntCC::UnsignedGreaterThanOrEqual, val, first_index);
        bx.ins().brnz(is_good_val, jt_block, &[]);//结果为true=1时发生跳转
        bx.seal_block(jt_block); // 密封新块
        cases_and_jt_blocks.push((first_index, jt_block, blocks));
    }
    ```

    当for的首次迭代结束后, `was_branch` 被置为true. 也就是说
    `contiguous_case_ranges` 剩下的每个组各自开辟一个新块.
    并在每个组的块最后插入一个无条件跳转到下个组的jump

        switch (val) {
         case '0': 
         case '1':
           break;

         case '5' :
           break;

         case '7': 
         case '8':
           break;
         }

    for循环之后: 生成跳转到default块的指令(和各个case都不匹配)

    ``` rust
    bx.ins().jump(otherwise, &[]);
    ```

### 继续 `build_search_tree` ()

当形成的分组\>3时,说明最终要形成的块的数量较多,此时直接生成跳转代码的效率太低,
要将比较逻辑用二叉树搜索的方式来进行.

上面这段代码为什么要用到stack+ while循环?

GPT: 这段代码通过使用一个栈结构和 while
循环来构建一个树形结构，其中每个节点都是一个基本块（block），该块的值是在
switch 表达式中被测试的值。在每个节点，根据该节点的连续 case
索引范围，会有一些分支指令用于测试测试值是否在该范围内。如果连续 case
索引范围小于或等于
3，则直接发出这些测试指令。否则，将节点拆分为两个子节点，并在中间插入一个条件分支，该分支将
switch
表达式值与分裂点的索引进行比较，从而确定应选择哪个子节点进行下一步分裂。
这个 while
循环实际上是在模拟一个深度优先搜索过程。在每一次迭代中，从栈顶弹出当前节点的信息，如果连续
case 索引范围小于等于
3，则在当前块中生成对应的分支指令，否则根据范围拆分当前节点，并将生成的子节点信息压入栈顶，这样就可以迭代生成整个搜索树。最终生成的
cases<sub>andjtblocks</sub> 向量包含了每个块的入口编号，以及每个 case
索引范围所对应的基本块和跳转表，这些信息将用于后续的跳转表生成过程。

先创建一个待处理stack,将 `contiguous_case_ranges` 不断切分后放入.

``` rust
let mut stack: Vec<(Option<Block>, Vec<ContiguousCaseRange>)> = Vec::new();
stack.push((None, contiguous_case_ranges));
```

下面是循环处理stack中的元素:

``` rust
while let Some((block, contiguous_case_ranges)) = stack.pop() {
    // ...
}
```

若取到元素的key不是空的, 则将焦点移到这个块上继续生成代码.

``` rust
if let Some(block) = block {
    bx.switch_to_block(block);
}
```

下面对取出来的 `contiguous_case_ranges` 按照元素个是分别进行处理.
不超过3时和上面的处理一样, 用 build<sub>searchbranches</sub> 生成代码

``` rust
if contiguous_case_ranges.len() <= 3 {
    Self::build_search_branches(
    bx,
    val,
    otherwise,
    contiguous_case_ranges,
    &mut cases_and_jt_blocks,
    );
}
```

当这个list太长时,顺序地为每个连续case值形成的组生成指令是低效的.(相当于线性查找)
因此要对这个list做切分,并且还能正确地跳转到这两部分.

``` rust
// ... 
else {
    let split_point = contiguous_case_ranges.len() / 2;
    let mut left = contiguous_case_ranges;
    let right = left.split_off(split_point); //从split_point处截断.

    /// 生成两个辅助块,作为左半部分,右半部分生成指令的起始块: 
    let left_block = bx.create_block();
    let right_block = bx.create_block();

    /// 选择跳往 左半部分/右半部分 ?
    let first_index = right[0].first_index; /// 右半部分第一个连续case组的最小case值
    let should_take_right_side = /// val是否 >= 这个值
    icmp_imm_u128(bx, IntCC::UnsignedGreaterThanOrEqual, val, first_index);
    bx.ins().brnz(should_take_right_side, right_block, &[]); /// 若是则跳往右半部分
    bx.ins().jump(left_block, &[]); /// 否则直接跳往左半部分

    /// 负责标记: 两个辅助块的前驱块(也就是当前块)的代码已经生成完毕
    bx.seal_block(left_block); 
    bx.seal_block(right_block);
    /// 将切分后的两个list加入到待生成指令的工作队列中,待之后的循环为其生成指令.
    stack.push((Some(left_block), left));
    stack.push((Some(right_block), right));
}
```

`build_search_tree` 的输出是用于产生jt<sub>table的信息</sub>.

所谓jt<sub>table</sub>, 在生成ir的开头处声明:

``` rust
jt0 = jump_table [block2, block3]
```

用法为通过br<sub>table指令</sub>:

``` rust
br_table 值, 落空块, jt_table
```

值就是jt<sub>table的索引</sub>,取值为 0,1,2,3, …
例如值为1时,跳转到jt0的第二个目标 block3 中.
当值无法对应jt<sub>table中的元素时</sub>,则跳转到落空块中(default分支).

### `build_jump_tables()`

``` rust
Self::build_jump_tables(bx, val, otherwise, cases_and_jt_blocks);
```

`jt_table` 用于生成 跳转到连续case值所对应的块

此函数的输入: 就是为了生成jt<sub>table准备的</sub>.
第二个Block是生成指令的起始块.

``` rust
cases_and_jt_blocks: Vec<(EntryIndex, Block, Vec<Block>)>,
```

此函数的主体是一个for循环, 反向取出元素 (first<sub>index从小到大</sub>)

``` rust
for (first_index, jt_block, blocks) in cases_and_jt_blocks.into_iter().rev() {
    /// ...
}
```

首先创建并初始化jump<sub>table</sub>. 并将焦点移到此连续case值所对应的块

``` rust
let mut jt_data = JumpTableData::new();
for block in blocks {
    jt_data.push_entry(block);
}
let jump_table = bx.create_jump_table(jt_data);

bx.switch_to_block(jt_block);
```

然后要将val和各个分支的连续case值比较转化为 jump<sub>table的索引</sub>.

例如: val=12, 一个case值形成的组是 \[10,11,12,13\]

为了生成正确的br<sub>table指令</sub>,要将 val-10 作为该指令的操作数,即:

``` rust
br_table  [u32值](val - first_index), otherwise块, jump_table
```

但这个 first<sub>index</sub> 的类型是 u128, 不能直接转为 Value所表示的值

1.  <span class="todo TODO">TODO</span> (val -
    first<sub>index</sub>)的类型转换???

    最后, 生成 br<sub>table</sub> 指令:

    ``` rust
    bx.ins().br_table(discr, otherwise, jump_table);
    ```

    br<sub>table</sub>() 是一个控制流指令，用于实现基于索引的跳转表。
    它有两个操作数：一个是作为索引的值，另一个是指向一系列块的表。指令会根据索引跳转到表中的相应块。

    ``` rust
    let selector = …; // a value to use as an index into the jump table
    let table = [block0, block1, block2, block3, block4];
    let default_block = …;
    let jump_dest = builder.br_table(selector, &table, default_block);
    ```

    在上面的示例中，如果 selector 是 0，那么 jump<sub>dest</sub> 将指向
    block0。如果 selector 是 4，那么 jump<sub>dest</sub> 将指向
    block4。如果 selector 不在 0..=4 的范围内，则 jump<sub>dest</sub>
    将指向 default<sub>block</sub>。

## ssa.rs

``` rust
#[test]
fn program_with_loop() 
```

``` asm
block0:
      x = 1;
      y = 2;
      z = x + y;
      jump block1
block1:
      z = z + y;
      brnz y, block3;
      jump block2;
block2:
      z = z - x;
      return y
block3:
      y = y - x
      jump block1
```

实际生成的ssa

``` asm
function u0:0() fast {

block0:
    v0 = iconst.i32 1
    v6 -> v0
    v1 = iconst.i32 2
    v2 = iadd v0, v1  ; v0 = 1, v1 = 2
    jump block1(v2, v1)  ; v1 = 2

block1(v3: i32, v4: i32):
    v5 = iadd v3, v4
    brnz v4, block3
    jump block2

block2:
    v7 = isub.i32 v5, v6  ; v6 = 1
    return v4

block3:
    v8 = isub.i32 v4, v6  ; v6 = 1
    jump block1(v5, v8)
}

```

如何构建一个Function呢? 首先不必多说, `Function::new()`
创建出一个对象func. 函数在IR中被表示为控制流图, 因此要有基本块.
这可以通过func.dfg数据流图来创建出一个块: `func.dfg.make_block()`.
并使用FuncCursor将其插入到函数布局中:

``` rust
cur.insert_block(block0)
```

块由一条条指令ins构成, 每条指令是一个表达式. 指令的添加也需要借助
`FuncCursor` 来完成,
添加完成一个表达式后,返回一个代表表达式结果的值value.

``` rust
let value =  {
    let mut cur =  FuncCursor::new(&mut func).at_bottom(block_curr);
    cur.ins().iadd(x_value,y_value)
}
```

``` rust
let x_ssa_value = cur.ins().iconst(I32,233);
```

而这种方式显然是没有包含变量定义的,
因此当使用变量时也无法从block中获得信息.

因此需要构建SSA, 一种记录了变量定义的IR. ssa的构建要借助SSABuilder.
使用ssa<sub>builder首先要声明当前所操作的块</sub>:

``` rust
ssa.declare_block(block0);
```

当需要记录变量定义时,

1.  创建一个"变量Variable": `Variable::new(N)`
2.  将插入函数基本块中的指令所返回的"值Value"记录下来, 并用 `def_var()`
    进行变量定义

``` rust
// 表示在块0中有定义: x_var <- x_ssa_value
ssa.def_var(x_var, x_ssa_value, block0);
```

当遇到变量的使用时: 用 `def_var()` 从当前块出发向前寻找变量的值

``` rust
let x_value = ssa.use_var(&mut func,x_var, I32, block0).0 
```

当移动到下一个块时,
除了创建新块,并将它记录到函数布局中,以及在ssa中声明后,还需要在ssas中声明它的前驱块:

``` rust
ssa.declare_block_predecessor(block1,pred_block,jump_ins);
```

其中的指令是前驱块中的跳转指令.

当一个块的所有前驱块全都被构建完成后,要将该块进行"密封":

``` rust
ssa.seal_block(block1,&mut func);
```

或者也可以在最后, 等到所有的block都创建完成后, 将所有的块密封:

``` rust
ssa.seal_all_blocks(&mut func)
```

### struct Function

``` rust
pub struct Function {

    pub name: UserFuncName, // 函数名, 主要是用于.clif文件

    pub stencil: FunctionStencil, // 函数模板, 核心部分

    pub params: FunctionParameters,
}
```

函数模板 : 数据和布局分离!

``` rust
pub struct FunctionStencil {
    /// ...

    /// Data flow graph containing the primary definition of all instructions, blocks and values.
    pub dfg: DataFlowGraph, //真正包含block的数据

    /// Layout of blocks and instructions in the function body.
    pub layout: Layout, // <<<==!!! 记录函数中块的顺序, 以及指令顺序.

    /// ...
}
```

``` rust
pub struct Layout {
    /// Linked list nodes for the layout order of blocks Forms a doubly linked list, terminated in
    /// both ends by `None`.
    blocks: SecondaryMap<Block, BlockNode>,

    /// Linked list nodes for the layout order of instructions. Forms a double linked list per block,
    /// terminated in both ends by `None`.
    insts: SecondaryMap<Inst, InstNode>,

    /// First block in the layout order, or `None` when no blocks have been laid out.
    first_block: Option<Block>,

    /// Last block in the layout order, or `None` when no blocks have been laid out.
    last_block: Option<Block>,
}
```

### SSABuilder: 实施ssa构造算法所需要的中间信息

``` rust
pub struct SSABuilder {
    // TODO: Consider a sparse representation rather than SecondaryMap-of-SecondaryMap.
    /// Records for every variable and for every relevant block, the last definition of
    /// the variable in the block.
    variables: SecondaryMap<Variable, SecondaryMap<Block, PackedOption<Value>>>,
    //记录了每个块中的变量定义

    /// Records the position of the basic blocks and the list of values used but not defined in the
    /// block.
    ssa_blocks: SecondaryMap<Block, SSABlockData>, // ssa算法中所需的块的信息

    /// Call stack for use in the `use_var`/`predecessors_lookup` state machine.
    calls: Vec<Call>,
    /// Result stack for use in the `use_var`/`predecessors_lookup` state machine.
    results: Vec<Value>,

    /// Side effects accumulated in the `use_var`/`predecessors_lookup` state machine.
    side_effects: SideEffects,

    /// Reused allocation for blocks we've already visited in the
    /// `can_optimize_var_lookup` method.
    visited: HashSet<Block>, // loop? 
}
```

``` rust
struct SSABlockData {
    // The predecessors of the Block with the block and branch instruction. // 前驱
    predecessors: PredBlockSmallVec,
    // A block is sealed if all of its predecessors have been declared.如果一个块的所有前任都已声明，则该块将被密封
    sealed: bool,
    // List of current Block arguments for which an earlier def has not been found yet.
    undef_variables: Vec<(Variable, Value)>,
}
```

### 继续 `program_with_loop()`

``` rust
let mut func = Function::new();
let mut ssa = SSABuilder::new();
let block0 = func.dfg.make_block();
let block1 = func.dfg.make_block();
let block2 = func.dfg.make_block();
let block3 = func.dfg.make_block();
```

真正创建构成了函数的4个block.

1.  `declare_block`

    创建在ssa构建中所需的块信息的结构:

    ``` rust
    ssa.declare_block(blockN)

    pub fn declare_block(&mut self, block: Block) {
        self.ssa_blocks[block] = SSABlockData {
        predecessors: PredBlockSmallVec::new(), /// 前驱
        sealed: false,  /// 是否seal
        undef_variables: Vec::new(), /// 尚未能找到定义的变量
        };
    }      
    ```

2.  block0:

    block0:

    ``` rust
    // block0
    ssa.declare_block(block0);
    ssa.seal_block(block0, &mut func); // 没有前驱, 立即seal
    let x_var = Variable::new(0);
    let x1 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block0);
        cur.ins().iconst(I32, 1)  //为函数在block0中生成指令 x = 1
    };
    ssa.def_var(x_var, x1, block0); // 在ssa中记录 x 的定义
    ```

    ``` rust
    let y_var = Variable::new(1);
    let y1 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block0);
        cur.ins().iconst(I32, 2)
    };
    ssa.def_var(y_var, y1, block0);
    ```

    调用use<sub>var从当前块开始寻找变量的定义</sub>

    ``` rust
    let z_var = Variable::new(2);
    let x2 = ssa.use_var(&mut func, x_var, I32, block0).0;
    let y2 = ssa.use_var(&mut func, y_var, I32, block0).0;
    let z1 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block0);
        cur.ins().iadd(x2, y2) // 生成 z = x+y 指令
    };
    ssa.def_var(z_var, z1, block0); // 在ssa中记录z在此块中的定义
    ```

    对应于 `jump block1` :

    ``` rust
    let jump_block0_block1 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block0);
        cur.ins().jump(block1, &[])
    };
    ```

3.  block1:

    ``` asm
    block1:
          z = z + y;
          brnz y, block3;
          jump block2;
    ```

    首先为ssa构建创建关于block1的信息的结构,
    然后声明从block0可以通过上面的jump指令跳转到block1.

    ``` rust
    ssa.declare_block(block1);
    ssa.declare_block_predecessor(block1, block0, jump_block0_block1);
    ```

    因为 block3也会跳到block1,因此它目前还不能标记为sealed.

    然后处理块中指令: 先利用ssa找出使用的变量的值,
    然后为函数生成代码,最后再用ssa记录变量的定义.

    ``` rust
    let z2 = ssa.use_var(&mut func, z_var, I32, block1).0;
    let y3 = ssa.use_var(&mut func, y_var, I32, block1).0;
    let z3 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block1);
        cur.ins().iadd(z2, y3)
    };
    ssa.def_var(z_var, z3, block1);
    ```

    接下来是brnz:

    ``` rust
    brnz y, block3;
    ```

    若y不为0 ,则跳到block3 :

    ``` rust
    let y4 = ssa.use_var(&mut func, y_var, I32, block1).0;

    let brnz_block1_block3 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block1);
        cur.ins().brnz(y4, block3, &[])
    };
    ```

    然后是 `jump block2` :

    ``` rust
    let jump_block1_block2 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block1);
        cur.ins().jump(block2, &[])
    };
    ```

4.  block2

    紧接着是

    ``` asm
    block2:
          z = z - x;
          return y
    ```

    仍然是 declare<sub>block</sub> + declare<sub>blockpredecessor</sub>

    ``` rust
    ssa.declare_block(block2);
    ssa.declare_block_predecessor(block2, block1, jump_block1_block2);
    ```

    并且,它的唯一前驱就是block1,因此可以被sealed.

    ``` rust
    ssa.seal_block(block2, &mut func);
    ```

    翻译 `z = z - x`

    ``` rust
    let z4 = ssa.use_var(&mut func, z_var, I32, block2).0; /// z 

    let x3 = ssa.use_var(&mut func, x_var, I32, block2).0; /// x 
    let z5 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block2);
        cur.ins().isub(z4, x3) /// z - x 
    };
    ssa.def_var(z_var, z5, block2); /// z = ...
    ```

    生成 `return y`

    ``` rust
    let y5 = ssa.use_var(&mut func, y_var, I32, block2).0;

    {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block2);
        cur.ins().return_(&[y5])
    };
    ```

5.  block3

    下面处理block3, 因为在block1中有 `brnz y block3`
    因此block1是其前驱.并且是其唯一前驱.

    ``` rust
    ssa.declare_block(block3);
    ssa.declare_block_predecessor(block3, block1, brnz_block1_block3);

    ssa.seal_block(block3, &mut func);
    ```

    ``` asm
    block3:
          y = y - x
          jump block1
    ```

    ``` rust
    /// y = y - x
    let y6 = ssa.use_var(&mut func, y_var, I32, block3).0;

    let x4 = ssa.use_var(&mut func, x_var, I32, block3).0;

    let y7 = {
        let mut cur = FuncCursor::new(&mut func).at_bottom(block3);
        cur.ins().isub(y6, x4)
    };
    ssa.def_var(y_var, y7, block3);
    ```

    ``` rust
    /// jump block1
    let jump_block3_block1 = {
       let mut cur = FuncCursor::new(&mut func).at_bottom(block3);
       cur.ins().jump(block1, &[])
       };
    ```

6.  seal block1

    现在block1的所有前驱已经处理完了,

    ``` rust
    ssa.declare_block_predecessor(block1, block3, jump_block3_block1);
    ssa.seal_block(block1, &mut func);
    ```

    接下来我们研究最后一个 `seal_block` 究竟做了什么?

    首先 对于block1, 它是编号为1的Block结构.

    此函数返回一个副作用结构.

    ``` rust
    pub fn seal_block(&mut self, block: Block, func: &mut Function) -> SideEffects {
        self.seal_one_block(block, func);
        mem::replace(&mut self.side_effects, SideEffects::new())
    }
    ```

    1.  `seal_one_block()`

        1.  对当前块中每个未定义变量执行 `predecessors_lookup()`

            进入到:

            ``` rust
            fn seal_one_block(&mut self, block: Block, func: &mut Function) {
                let block_data = &mut self.ssa_blocks[block];
                /// ...
            ```

            block1的blockdata:

            ``` rust
            predecessors: PredBlockSmallVec,/// block0, block3

            sealed: bool, /// 值为假

            undef_variables: Vec<(Variable, Value)>,
            /// z(2)=3, y(1)=4, x(0)=6,
            ```

            继续:

            ``` rust
              /// ...
              // Extract the undef_variables data from the block so that we
              // can iterate over it without borrowing the whole builder.
              let undef_vars = mem::replace(&mut block_data.undef_variables, Vec::new());

              // For each undef var we look up values in the predecessors and create a block parameter
              // only if necessary.
              for (var, val) in undef_vars {
                  let ty = func.dfg.value_type(val);
                  self.predecessors_lookup(func, val, var, ty, block);
              }
              self.mark_block_sealed(block);
            }
            ```

            `z(2) = 3`

        2.  `predecessors_lookup()`

            ``` rust
            self.predecessors_lookup(func, val, var, ty, block);
            ```

            其实现为:

            ``` rust
            self.begin_predecessors_lookup(value=3, block1 );
            self.run_state_machine(func, z(2) , ty)
            ```

            1.  `begin_predecessors_lookup()` 将块的前驱压入调用栈

                ``` rust
                fn begin_predecessors_lookup(&mut self, sentinel: Value, dest_block: Block) {
                    self.calls
                    .push(Call::FinishPredecessorsLookup(sentinel=3, dest_block=block1));
                    // Iterate over the predecessors.
                    let mut calls = mem::replace(&mut self.calls, Vec::new());
                    calls.extend(
                    self.predecessors(dest_block)
                        .iter()
                        .rev()
                        .map(|&PredBlock { block: pred, .. }| Call::UseVar(pred)),
                    );
                    self.calls = calls;
                }
                ```

                `self.calls` :

                | Call::UseVar(block0)                         |
                |----------------------------------------------|
                | Call::UseVar(block3)                         |
                | Call::FinishPredecessorsLookup(val=3,block1) |

            2.  `run_state_machine()` 开始

                1.  UseVar(): 在当前块中寻找,找不到则为前驱安排查找任务

                    准备好任务栈后, 正式由下面的方法来执行. 此时入参var
                    表示变量z(2)

                    ``` rust
                    fn run_state_machine(&mut self, func: &mut Function, var: Variable, ty: Type) -> Value 
                    ```

                    核心逻辑是用while不断从calls栈中弹出任务:

                    ``` rust
                    while let Some(call) = self.calls.pop() {
                        Call::UseVar(ssa_block) => {
                        ///...
                        },
                        Call::FinishSealedOnePredecessor(ssa_block) => {
                        ///...
                        },
                        Call::FinishPredecessorsLookup(sentinel, dest_block) => {
                        ///...
                        },
                    }
                    ```

                    按照之前画出的调用栈:

                    首先取出的元素是 `Call::UseVar(block0)`,
                    先尝试从当前块block0中找到z的定义,找到终止此次循环.否则尝试用
                    `use_var_nonlocal` 从前驱中继续寻找.

                    ``` rust
                    Call::UseVar(block0) => {
                        if let Some(var_defs) = self.variables.get(变量z) {
                        if let Some(val) = var_defs[block0].expand() {
                            self.results.push(val);
                            continue;
                        }
                        }
                        self.use_var_nonlocal(func, var, ty, block0);
                    }
                    ```

                    这里能在block0中找到z的定义, 因此提前跳出.

                    下一次从calls中取出的是 `Call::UseVar(block3)`,
                    这次不能在block3本身中找到z的定义,因此要借助
                    `use_var_nonlocal` 向calls中压入新任务,
                    用来到block3的前驱中寻找z的定义.

                2.  `use_var_nonlocal()` 将前驱作为任务压入调用栈

                    ``` rust
                    fn use_var_nonlocal(&mut self, func: &mut Function, var: Variable, ty: Type, block: Block)
                        /// var == z
                        /// block == block3
                    ```

                    此函数被特意的分成两段,主要是为了不触犯借用规则.
                    第一部分返回一个值作为flag来指导第二部分的走向.

                    1.  Part1

                        case指示了当前块能否继续向回查找(seal?)
                        或是此块是否有多个前驱

                        ``` rust
                        let optimize_var_lookup = self.can_optimize_var_lookup(block);
                        let data = &mut self.ssa_blocks[block];

                        let case = if data.sealed { /// 此节点的所有前驱是否已经构造完成?
                            // Optimize the common case of one predecessor: no param needed.
                            if optimize_var_lookup { /// 此节点只有一个前驱,且该前驱不处于环中
                            UseVarCases::SealedOnePredecessor(data.predecessors[0].block)
                            } else { /// 多个前驱
                            // Break potential cycles by eagerly adding an operandless param.
                            let val = func.dfg.append_block_param(block, ty);
                            UseVarCases::SealedMultiplePredecessors(val, block)
                            }
                        } else { /// 仍有前驱尚未构造完成,此变量的定义不能查找
                            let val = func.dfg.append_block_param(block, ty);
                            data.undef_variables.push((var, val)); // 将这个块中尚不能找到定义的
                            UseVarCases::Unsealed(val)
                        };
                        ```

                    2.  `can_optimize_var_lookup()`:
                        只有一个前驱,且前驱不在环中

                        ``` rust
                        ///  返回true: block只能有一个前驱,且它不处在一个环中.
                        ///  用visited: HashSet<Block> 实现有无环检测

                          fn can_optimize_var_lookup(&mut self, block: Block) -> bool {
                          // Check that the initial block only has one predecessor. This is only a requirement
                          // for the first block.
                          if self.predecessors(block).len() != 1 {
                              return false;
                          }

                          self.visited.clear(); /// 置为空
                          let mut current = block;

                          loop {
                              let predecessors = self.predecessors(current);

                              // We haven't found the original block and we have either reached the entry
                              // block, or we found the end of this line of dead blocks, either way we are
                              // safe to optimize this line of lookups.
                              if predecessors.len() == 0 {
                              return true;
                              }

                              // We can stop the search here, the algorithm can handle these cases, even if they are
                              // in an undefined island.
                              if predecessors.len() > 1 {
                              return true;
                              }

                              let next_current = predecessors[0].block;
                              if !self.visited.insert(current) { /// 将当前节点插入,若返回false,则代表重复插入.
                              return false;
                              }
                              current = next_current;
                          }
                          }
                        ```

                    3.  `append_block_param(block, ty)`

                    4.  Part2
