# [定义C++迭代器](https://users.cs.northwestern.edu/~riesbeck/programming/c++/stl-iterator-define.html)

所有的STL容器都定义了：
- 该容器的迭代器类型，如：iterator、const_iterator
- 该容器的begin() end() 方法



没有定义上面两种的容器被看做二等公民，他们不能和泛型算法一起使用，为你的容器定义迭代器类型和begin、end方法，无论他们是否是泛型容器



## 来自被嵌套的STL容器的迭代器

若你的容器中使用了STL容器作为内部数据成员，那么只需要将迭代器和两个方法的实现托付给STL容器即可。

例如，假如你有一个类CourseList，它表示学生参加的课程的列表，在其内部使用了一个Student的Vector来存储课程列表。对这样的自定义容器只需要依赖STL容器Vector即可：

```c++
class CourseList {
private:
	  typedef vector<Student> StudentList;
	  StudentList students;
    
public:
	  typedef StudentList::iterator   iterator;
	  typedef StudentList::const_iterator 	const_iterator;
    
	  iterator begin() { return students.begin(); }
	  iterator end() { return students.end(); }
  ...
};
```

换句话讲，我们做的仅仅是：

- 将CourseList的iterator定义为StudentList::iterator，将其const_iterator定义为Student::const_iterator
- 让CourseList的begin() end() 方法直接返回其内部容器StudentList的begin() end() 方法



## 指针实现迭代器

C指针是合法的迭代器，因此若你的内部用来存放数据的容器是一个C数组，你需要做的仅仅就是返回指针。例，我们将StudentList实现为一个C数组：

```C++
class CourseList {
private:
  typedef Student  StudentList[100];
  StudentList  students; 
    
public:
	  typedef Student *  iterator; 
	  typedef const Student *  const_iterator; 
    
	 iterator begin() { return &students[0]; } //
 	 iterator end() { return &students[100]; } //
};
```

## 用已有迭代器来定义新迭代器



有时候需要一个普通容器的迭代器的变体，比如该迭代器可以计数，或者迭代器可以检查是否在一个合法范围

定义这种特殊的迭代器通常需要使用委托模式，新迭代器的构造函数要初始化某种存在的迭代器，以及其它所需要的信息，并将某种已有的迭代器作为私有成员变量，然后这个自定义的迭代器的operator++ operator* 只是添加一些额外的功能然后调用那个已有的迭代器变量的++ 与* 操作符



## 为新容器定义迭代器 

最后一种情况是为一个新类型的容器定义迭代器。

STL中不使用类的层次结构和继承，因此当定义一个迭代器时，无法以“迭代器超类”为基础开始定义。不过只要定义了部分或全部的迭代器操作符，它就可以称为是迭代器。

基本的迭代器操作符如下：

- operator*
- operator++
- operator!=



作为容器的例子，下面先实现一个环形队列：

## 环形队列

环形队列是一个有限大小的队列，并且它不会变满或超出固定大小，相反地，新元素会覆盖旧元素，一个环形队列能保持对数字流中最新的那些值的追踪，并且在添加新元素是自动地将旧元素抛弃。比如，环形队列可能用在求最近的N个数字的平均值。

我们将实现一个这样的环形队列：

```C++
RingQueue< int, 5 >  ringQueue;//创建了五个元素的环形队列
```

像普通的队列一样，可以向队末压入元素，从队首弹出元素，但也有一些差别：

- 环形队列只保存最近压入的N个元素
- 使用push_back() 和pop_front()来代替push() pop()以便支持泛型算法和`back_inserter`
- push_front()作用在已满的环形队列时会将最旧的元素移除（第一个）并添加新的元素
- begin() end()支持用迭代器访问队列



常规的实现环形队列的方法时用数组和两个特殊的数字：

- myBuffer：N个元素的数组
- myBegin：标识队首的数字
- mySize：标识队列中有多少元素

myBegin在初始状态时为0，即数组的第一个元素。环形队列的队尾可以通过下面的计算得到：
$$
myEnd  = (myBegin + mySize)\ \% \  N
$$
可以定义如下的访问器：

- front() ：myBuffer[myBegin]，当mySize!=0时
- back() ：myBuffer[myEnd],当mySize!=0时

改变myBegin和mySize的规则：

- pop_front()增加myBegin并减少mySize
- push_back() 将值存放到myBuffer[myEnd]并增加mySize直到N为止，此后它仍将值存放到myBuffer[myEnd]，并增加myBegin
- 当myBegin到达N时，它将被重设为0；mySize不会超过N，也不会小于0



例子：

![image-20211017135138809](C++迭代器.assets/image-20211017135138809.png)



## 环形队列的迭代器

从直观来讲，我们想把begin()和end()函数定义为：

- begin(): &myBuffer[myBegin]
- end():&myBuffer[myEnd]



但这么做是有问题的

```C++
RingQueue<int, 4> rq;

for ( int i = 0; i < 10 ++i ) rq.push_back( i * i );

cout << "There are " << rq.size() << " elements." << endl;
cout << "Here they are:" << endl;
copy( rq.begin(), rq.end(),
      ostream_iterator<int>( cout, "\n" ) );
cout << "Done" << endl;
 
```

输出：

```
There are 4 elements.
Here they are:
Done
 
```

并不能正常输出。

注意到当环形队列满的时候，myBegin=myEnd，因此下面这样的代码会失效：

```C++
while ( rq.begin() != rq.end() ) ...
 
```

一个明显的正确方法是维护一个以myBegin为基准的偏移量：

- 偏移量=0 意味着在队列的开始
- 偏移量为mySize表示在队尾
- 偏移量介于0和mySize之间的表示在队列中

因此环形队列的迭代器必须包含两个东西：

1. 对环形队列的引用
2. 一个记录偏移量的变量

其运算符如下：

- `operator!=`为真当两个迭代器包含着不同的环形队列或有不同的偏移量
- `operator++` 增加偏移量
- `operator*` 返回索引为(myBegin+offset)%N的数组元素



## 一些要注意的C++语法细节



### 细节1：让容器和迭代器建立联系

容器要和其迭代器建立联系：

- 在容器的begin() end()方法中，需要构造并返回迭代器
- 在迭代器中，要有一个数据成员是对容器的引用

二者的相互引用意味着我们要在迭代器之前定义容器，并且迭代器常常需要访问容器的私有成员才能完成功能。

出于这些原因，可归纳处定义容器和其迭代器的典型模式：

- 将迭代器的声明前置
- 定义容器类
- 在容器中将迭代器类声明为友元类
- 定义迭代器类

代码如下：

```C++
// 迭代器声明前置
 
template < class T, int N > class RingIter;
 
 
// 定义容器，并使其迭代器成为友元 
 
template < class T, int N >
class RingQueue {
 
  friend class RingIter< T, N >;
  ...
};
 
 
// 定义迭代器类
 
template < class T, int N >
class RingIter {
...
};
 
```



### 细节2：使容器的迭代器易于使用

某些STL函数，如：back_inserter()，需要一些关于容器的关键信息才能构建迭代器，这些信息由容器类开头的一系列typedef来传达，例如容器类应定义类型value_type和iterator使得其它函数可以知道这个容器可以装入什么类型的对象，以及该容器的迭代器类型是什么

```C++
  typedef RingIter<T, N> iterator;
  typedef ptrdiff_t difference_type;
  typedef size_t size_type;
  typedef T value_type;
  typedef T * pointer;
  typedef T & reference;
 
```



### 细节3：begin()和end()

容器中的主要负责返回迭代器的函数是begin()和end()。通常，它们只是调用迭代器类的构造器，构造器一般最少需要两个参数：

- 容器自身
- 一个能标识迭代器指向何处的参数

```C++
iterator begin() { return iterator( *this, 0 ); }
 
iterator end() { return iterator( *this, mySize ); }
 
```



### 细节4：在迭代器中存储容器的引用



```C++
template < class T, int N >
class RingIter {
private:
  RingQueue<T, N> & myRingQueue;//对实际容器的引用
  int mySize;
public:
  RingIter( RingQueue & rq, int size ) 
   : myRingQueue( rq ), mySize ( size ) //为了能让引用类型的成员变量初始化
  {}
 
```



### 细节5：为迭代器定义operator!=()

若迭代器的数据成员只是指针（表示容器）以及int等基本类型，则默认的operator==和operator!=就够用了



### 细节6：为迭代器定义operator*()

```C++
*dest = *source;
```

*dest被称为左值，即能存储其它值的东西。

定义operator*意味着返回一个对某位置的引用，这确保了无论对迭代器的解引用发生在等号的哪一侧都使其是合法的（引用也确保了该对象一定不是NULL的）

```C++
T & operator*() { return myRingQueue[ myIncrement ]; }
 
```



### 细节7：为迭代器定义operator++()

自增运算符有两种调用方式，一种是前置，一种是后置：

- 前置：++iter
- 后置：iter++

前置++ 的实现比较简单，只需要将迭代器中表示位置的变量增加、设为下一位置即可，并返回迭代器本身。

```C++
iterator & operator++() { ++myOffset; return *this; }
 
```

后置的版本有些令人困惑，原因有二：

- 如何区分后置++与前置++
- 后置++必须修改迭代器，并且要将修改之前的迭代器返回

第一个问题是将后置++的参数列表设为一个没有实际用处的int

第二个问题需要创建一个修改前的迭代器的拷贝并将其返回

```C++
iterator operator++ ( int ) //只能返回值类型。而不能返回引用
{
  RingIter<T, N> clone( *this );//调用复制构造函数，拷贝一份原迭代器
  ++myOffset; //修改当前迭代器
  return clone;
}
```



### 其它C++语法上的细节

- const iterator:我们需要定义两类迭代器，一种就是上面的常规迭代器，另一种是const迭代器，它唯一的区别是其成员函数返回的引用都是常引用

  ```C++
  typedef RingIter<T, N> iterator;
  
  typedef RingCIter<T, N> const_iterator;
  
  ...
  
  iterator begin() { return iterator( *this, 0 ); }
  
  iterator begin() const { return const_iterator( *this, 0 ); }
  ```

- 反向迭代器：我们需要定义rbegin()和rend()来返回反向迭代器；并且也需要定义其const版本
- **Iterator traits**：某些复杂的STL算法和适配器通过查看包含了迭代器特质traits的数据结构来确定可以用对容器和其迭代器做哪些事。traits表示诸如：这个迭代器是双向的，指向整数类型的..它是迭代器数据成员的一部分。

