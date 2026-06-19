# [为函数添加别名](https://stackoverflow.com/questions/192049/is-it-possible-to-have-an-alias-for-the-function-name-in-lisp)

``` commonlisp
(defalias 'newname 'oldname)
```

# 在org模式下快速插入代码块

在org中插入一个代码块比起markdown要麻烦不少:

`#+begin_src xx` `#+end_src`

为了快速插入代码块, 我们要写两个函数:

1.  `insert-empty-code-block` : 插入指定语言的代码块.
    先输入代码类型,例如cpp, 然后 `M-x insert-empty-code-block`,
    这样就能生成指定类型的代码块.

2.  `insert-code-block` : 将选中文本用代码块包裹起来 先选中某段文本,然后
    `M-x insert-code-block`, 然后输入可选参数: 代码类型. (eg: cpp)

首先来分析第一个函数的实现. 这个功能类似于idea的.var,
首先要读取光标处的"单词", 比如 `cpp`, 通过学习李杀的教程,发现可以使用
`thing-at-point` 来获取光标处的单词, (thing-at-point '选择范围 )
这个选择范围有:

``` commonlisp
'word : 一个单词, "emacs-lisp"不是一个单词
'symbol : 一个符号, 比如 emacs-lisp
'line : 一行
更多的范围可以查询 c-h f
```

成功读取代码块的类型后，还需要将其删掉并添加代码块。删掉某个范围的文本可以使用
`(delete-region start end)` ,
因此我们需要知道刚才拿到的文本的开始和结束位置,
这需要函数(bounds-of-thing-at-point '范围) 它会返回一个list = (start
end).

第二个函数的实现难处在于, 需要能操纵用户选中的文本,
并且在minibuffer中传入一个可选参数作为代码块的类型. 可选参数可以用
`&optional args` ,以及 `(interactive "s-->:")` 来接收.
剩下的问题就是如何操作用户选中的文本了. 首先要先保存并删除选中的文本,
然后在前后加上代码块的开始和结束代码后再插入回去.
先来看如何保存选中文本, 要保存这些文本, 首先要知道其位置: 开始和结束,
可以用两个函数来获取选中区域的开始和结束位置:

`(region-beginning )` `(region-end )`

然后要从这个位置将文本保存到一个变量中,
`(buffer-substring-no-properties start end)`
这个函数可以将buffer的一部分不保留属性地拷贝到变量中.
删除选中区域在有了开始和结束位置后就能用 `(delete-region start end)`
实现了.

这里需要注意的是输入的可选参数需要转换一下才能作为字符串类型来使用.这里正好用
`concat` 连接了一个空格, 从而将它看做字符串.

``` commonlisp
;;;;;;;;;;;;;Org模式下将选中文本放入代码块;;;;;;;;;;;;;
(setq previous-type "")

(defun insert-and-update-type-str (type-str)
   (if  (string-equal " " type-str)
    (insert  previous-type)

     (insert type-str)
     (setq previous-type type-str))
   )

(defun insert-code-block(&optional type)
  (interactive   "sEnter code type: "  )
  (let* ((type-str (concat " " type))
     (s (region-beginning))
     (e (region-end))
     (code-block (buffer-substring-no-properties s e)))
    (delete-region s e)
    (insert "#+begin_src")
    (insert-and-update-type-str type-str)          
    (insert "\n")
    (insert code-block)
    (insert "\n#+end_src\n")
    )
  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun insert-empty-code-block()
  (interactive)
  (let* ((type-str (concat " " (thing-at-point 'symbol)))
     (bounds (bounds-of-thing-at-point 'symbol))
     (s (car bounds))
     (e (cdr bounds))
    )

    (if (not (eq s e ))
    (delete-region s e)
  )

    (insert "#+begin_src")
    (insert-and-update-type-str type-str)
    (insert "\n")
    (insert "\n#+end_src\n")
    )
  )

 (global-set-key (kbd "<f1>" ) 'insert-empty-code-block) 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

```

**参考**

- <https://segmentfault.com/a/1190000039313306>

- <https://www.jianshu.com/p/65b271c1dabf>

- <http://xahlee.info/emacs/emacs/elisp_thing-at-point.html>

# 生成相对路径来指向org的主题

``` commonlisp
;;;;;;;;;;;;;;;用相对路径从当前目录访问项目根目录;;;;;;;;;;;;;;;;;
(setq org-confirm-babel-evaluate nil) ;; org模式下运行代码无需手动确认
(require 'project)
(defun count-dir (str)
  "Count the number of '/' in the STR."
  (let* ( (clist (mapcar #'char-to-string str) )
      (cnt 0) )
    (dolist (ch clist  cnt)
      (if (string= ch "/" )    
      (setq cnt (+ 1 cnt))
    ))))

(defun path-diff ()
  "The current directory position is from the depth of the root directory of the project."
  (let* ( (current (expand-file-name(concat "" (format default-directory))))
      (root (expand-file-name (locate-dominating-file "." "mytheme.setup" ))))
    (message "%s\n" current)
    (message "%s\n" root) 
    (- (count-dir current) (count-dir root) )
    )
  )

(defun rel-path ()
  "Return to the relative path to the root directory of the project."
  (let* ( (cnt (path-diff))
      (path "" )   )
    (while (> cnt 0)
      (setq path (concat path  "../" ) )
      (setq cnt (- cnt 1 )))
    (concat path "") 
    )
  )

(defun org-setup-mytheme( )
  (interactive) 
  (insert   (concat "#+include: "  (rel-path)  "mytheme.setup \n"))
  )

```

在org文件头部执行： `org-setup-mytheme`

    #+include: ./mytheme.setup

``` org
# -*- mode: org; -*-
#+OPTIONS: html-style:nil  html-postamble:nil


src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <link rel=\"stylesheet\" type=\"text/css\" href=\"" (rel-path) "org-html-themes/src/bigblow_theme/css/htmlize.css\"/>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <link rel=\"stylesheet\" type=\"text/css\" href=\"" (rel-path) "org-html-themes/src/bigblow_theme/css/bigblow.css\"/>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <link rel=\"stylesheet\" type=\"text/css\" href=\"" (rel-path) "org-html-themes/src/bigblow_theme/css/hideshow.css\"/>")}


src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/jquery-1.11.0.min.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/jquery-ui-1.10.2.min.js\"></script>")}


src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/jquery.localscroll-min.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/jquery.scrollTo-1.4.3.1-min.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/jquery.zclip.min.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/bigblow.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/bigblow_theme/js/hideshow.js\"></script>")}
src_emacs-lisp[:results raw]{(concat "#+HTML_HEAD: <script type=\"text/javascript\" src=\"" (rel-path) "org-html-themes/src/lib/js/jquery.stickytableheaders.min.js\"></script>")}
```
