# linux 核心设计笔记

C + 算法 + 概率统计 + 编译器 + OS + 处理器

## 2023-2-13

并行程式的可扩展性: 随着 cpu 核数的增长, 吞吐量有显著的增长.

浮点数的问题:

``` cpp
#include <stdio.h>
int main() {
  float sum = 0.0f;
  for (int i = 0; i< 10000; i++) sum += i + 1;
  printf("sum: %f \n", sum);
  return 0;
}
```

1 + 2 + .. + 10000 != 50005000

将float改成double结果是对的, 但在更大的数值同样会发生错误.

改善精确度:

``` cpp
#include <stdio.h>
int main() {
  float sum = 0.0f;
  float corr = 0.0f; // 修正值:用来应对舍入问题
  for (int i = 0; i< 10000; i++){
    float y = (i+1) - corr; 
    float t = sum + y;
    corr = (t - sum) - y;
    sum = t;
  }
  printf("sum: %f \n", sum);
  return 0;
}
```

浮点数是

逐字翻译成 C 不是 编程!

- x \>=0 , 则 mask = 0x00000000, xor 后数值不变.
- x \< 0, 则 mask = 0xffffffff = -1, 全1 xor 数值后,则会翻转每个位.
  因此也就是将x - 1 后按位取反.

``` cpp
#include <stdint.h>
int32_t abs(int32_t x) { // 求绝对值
  int32_t mask = (x >> 31); // 31个零 ++ 符号位
  return (x + mask) ^ mask; // 无分支 !!! 
}
```

但这样的写法是有问题的:

``` rust
abs(i32::MIN) ==> i32::MIN !!!
```

ASLR: address space layout randomization (地址随机化)

``` cpp
uintptr_t _mi_random_init(uintptr_t seed) {
  // ASLR 会随机安排此函数的地址.
  uintptr_t x = (uintptr_t) ((void*)& _mi_random_init);
  //...
}
```

如果不开启ASLR, 则程序中的函数的地址是固定的.很容易被buffer
overflow攻击.

linux很少用 快排 进行排序.最坏时间为 O(N<sup>2</sup>) eg: top,
对进程进行排序.

linux内置的linked list是环状的.

积分arctan(x) = ??

1:34:00 -\> 诚实面对, 缺啥补啥

使用bitwise(位运算)降低空间开销:

``` cpp
#include <bits/stdc++.h>
using namespace std;

// index >> 5 : index / 32
// index & 31 : index % 32

bool checkbit(int array[],int index) {
  return array[index >> 5] & (1 << (index & 31))
}

void setbit(int array[],int index){
  array[index>>5] |= (1 << (index & 31));
}
```

## 第一周课程

阅读论文, 并重现. 而不是做摘要/简报.

### 二进制表示

- 自然编码 最高位表示符号, 剩下的表示数字的绝对值. eg :
  `-1 = 1000 0001`, `1 = 0000 0001` .

- 一补数(反码) 一个数字的相反数即反码 TCP/UDP中仍有使用.

- 二补数
