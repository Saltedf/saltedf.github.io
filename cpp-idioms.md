# 不用#define

## static const / enum （int常量）

## 模板inline函数

    template <typename T,...>
    inline RetType func(const T& a, ..... ){

    }

# const

## const的出现位置

- 修饰返回类型 能修饰尽量修饰，除非是涉及返回引用/指针
  （这种多出现于非const版本成员函数中）

- 修饰成员函数（后置）

优先定义const版本的成员函数，否则还需要一个非const版本的。
当同时存在二者且代码相同时，用const版本的实现非const版本（
`static_cast<const A&>` + `const_cast<Rettype>` )

(反之则不行，因为非const版本的可能会修改内部成员；而用const实现非const则可以额外再修改某些数据）

物理常量性 不修改非 `static` 成员即可

逻辑常量性 允许 `mutable` 的成员被修改；不能返回能修改内部的引用/指针

# constexpr

## 何处需要填入一个const exp

- 数组的大小

- 作为模板参数的int

std::array / std::tuple
