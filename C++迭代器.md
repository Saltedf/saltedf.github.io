# 定义C++迭代器

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
RingQueue< int, 5 >  ringQueue;
```

