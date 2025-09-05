This is an Org mode document.

**Org mode** is a easy-to-write *plain text* formatting syntax for
authoring LaTeX documents, creating Web pages and much more!

<script src="http://platform.twitter.com/widgets.js"></script>
<a href="https://twitter.com/share" class="twitter-share-button" data-via="f_niessen">Tweet</a>

# Basics

## Biggest heading

New chapter.

### Bigger heading

New section.

#### Big heading

New sub-section.

#### Text breaks

A single newline has no effect. This line is part of the same paragraph.

But an empty line

demarcates paragraphs.

By entering two consecutive backslashes, you can force to break lines  
without starting a new paragraph.

For an horizontal line, insert at least 5 dashes: this is some text
above an horizontal rule

------------------------------------------------------------------------

and some text below it.

#### Numbered headings

You can create numbered headings up to a certain level by setting an
option:

``` org
#+OPTIONS: H:4
```

### Text width

One morning, when Gregor Samsa woke from troubled dreams, he found
himself transformed in his bed into a horrible vermin. He lay on his
armour-like back, and if he lifted his head a little he could see his
brown belly, slightly domed and divided by arches into stiff sections.
The bedding was hardly able to cover it and seemed ready to slide off
any moment. His many legs, pitifully thin compared with the size of the
rest of him, waved about helplessly as he looked.

## Lists

Org markup allows you to create bulleted or numbered lists. It allows
any combination of the two list types.

### Unordered lists

Itemized lists are marked with bullets. They are convenient to:

- organize data, and
- make the document
  - prettier, and
  - easier to read.

Create them with a minus or a plus sign.

### Ordered lists

Enumerated lists are marked with numbers or letters:

1.  First element
    1.  First sub-item
    2.  Last sub-item
2.  Second element

You can have ordered lists with jumping numbers:

1.  First
2.  Second
3.  Jump to 5th

### Definition lists

Definition list  
List containing definitions.

Term to define  
Explication of the term.

### Checkboxes

- [ ] First item not checked
- [ ] Second item half done
  - [ ] Another first
  - [ ] Another second
- [x] Third item checked

## Miscellaneous effects

### Include Org files

You can include another Org file and skip its title by using the
`:lines` argument to `#+INCLUDE`:

``` org
#+INCLUDE: chapter1.org :lines "2-"
```

> [!NOTE]
> File inclusion, through INCLUDE keywords, is an **export-only
> feature**.

### Inline HTML

You can include raw HTML in your Org documents and it will get kept as
HTML when it's exported. XXX

Text can be preformatted (in a fixed-width font).

It is especially useful for more advanced stuff like images or tables
where you need more control of the HTML options than Org mode actually
gives you.

Similarly, you can incorporate JS or do anything else you can do in a
Web page (such as importing a CSS file).

You can create named classes (to get style control from your CSS) with:

``` example
#+begin_info
*Info example* \\
Did you know...
#+end_info
```

You can also add interactive elements to the HTML such as interactive R
plots.

Finally, you can include an HTML file verbatim (during export) with:

``` org
#+INCLUDE: file.html html
```

Don't edit the exported HTML file!

### Inline LaTeX

You can also use raw LaTeX. XXX

Text can be preformatted (in a fixed-width font).

### Centered text

<div class="center">

This text is centered!

</div>

## Code blocks

### Line numbers

Both in `example` and in `src` snippets, you can add a `-n` switch to
the end of the `begin` line, to get the lines of the example numbered.

``` commonlisp
(defun org-xor (a b)
  "Exclusive or."
```

If you use a `+n` switch, the numbering from the previous numbered
snippet will be continued in the current one:

``` commonlisp
(if a (not b) b))
```

In literal examples, Org will interpret strings like `(ref:name)` as
labels, and use them as targets for special hyperlinks like `[[(name)]]`
(i.e., the reference name enclosed in single parenthesis). In HTML,
hovering the mouse over such a link will remote-highlight the
corresponding code line, which is kind of cool.

You can also add a `-r` switch which removes the labels from the source
code. With the `-n` switch, links to these references will be labeled by
the line numbers from the code listing, otherwise links will use the
labels with no parentheses. Here is an example:

    (save-excursion                  ; (ref:sc)
      (goto-char (point-min)))       ; (ref:jump)

In line <span class="spurious-link" target="(sc)">*(sc)*</span>, we
remember the current position. <span class="spurious-link"
target="(jump)">*Line (jump)*</span> jumps to `point-min`.

### Output

The output from the **execution** of programs, scripts or commands can
be inserted in the document itself, allowing you to work in the
*reproducible research* mindset.

#### Text

A one-liner result:

``` bash
date +"%Y-%m-%d"
```

``` example
2014-03-15
```

#### Graphics

Data to be charted:

| Month | Degrees |
|-------|---------|
| 1     | 3.8     |
| 2     | 4.1     |
| 3     | 6.3     |
| 4     | 9.0     |
| 5     | 11.9    |
| 6     | 15.1    |
| 7     | 17.1    |
| 8     | 17.4    |
| 9     | 15.7    |
| 10    | 11.8    |
| 11    | 7.7     |
| 12    | 4.8     |

Code:

``` r
plot(data, type="b", bty="l", col=c("#ABD249"), las=1, lwd=4)
grid(nx=NULL, ny=NULL, col=c("#E8E8E8"), lwd=1)
legend("bottom", legend=c("Degrees"), col=c("#ABD249"), pch=c(19))
```

The resulting chart:

![](../../images/Rplot.png)

#### R code block

``` r
library(ggplot2)
summary(cars)
```

Plot:

``` r
library(ggplot2)
qplot(speed, dist, data = cars) + geom_smooth()
```

## Inline code

You can also evaluate code inline as follows: 1 + 1 is `1 + 1`.

## Notes at the footer

It is possible to define named footnotes[^1], or ones with automatic
anchors[^2].

## Formatting text

### Text effects

*Emphasize* (italics), **strongly** (bold), and ***very strongly***
(bold italics).

Markup elements could be nested: this is *italic text which contains
<u>underlined text</u> within it*, whereas <u>this is normal underlined
text</u>.

Markup can span across multiple lines, by default **no more than 2**:

\*This is not bold\*

Other elements to use sparingly are:

- monospaced typewriter font for `inline code`
- monospaced typewriter font for `verbatim text`
- ~~deleted~~ text (vs. <u>inserted</u> text)
- text with<sup>superscript</sup> (for example: `m/s^{2}` gives
  m/s<sup>2</sup>)
- text with<sub>subscript</sub> (for example: `H_{2}O` gives
  H<sub>2</sub>O)

### Quotations

Use the `quote` block to typeset quoted text.

> Let us change our traditional attitude to the construction of
> programs: Instead of imagining that our main task is to instruct a
> computer what to do, let us concentrate rather on explaining to human
> beings what we want a computer to do.
>
> The practitioner of literate programming can be regarded as an
> essayist, whose main concern is with exposition and excellence of
> style. Such an author, with thesaurus in hand, chooses the names of
> variables carefully and explains what each variable means. He or she
> strives for a program that is comprehensible because its concepts have
> been introduced in an order that is best for human understanding,
> using a mixture of formal and informal methods that reinforce each
> other.
>
> — Donald Knuth

A short one:

> Everything should be made as simple as possible, but not any simpler –
> Albert Einstein

In a `verse` environment, there is an implicit line break at the end of
each line, and indentation and vertical space are preserved:

Everything should be made as simple as possible,  
but not any simpler – Albert Einstein

Typically used for quoting passages of an email message:

\>\> This is an email message with "nested" quoting. Lorem ipsum dolor
sit amet,  
\>\> consectetuer adipiscing elit. Aliquam hendrerit mi posuere
lectus.  
\>\> Vestibulum enim wisi, viverra nec, fringilla in, laoreet vitae,
risus.  
\>  
\> Donec sit amet nisl. Aliquam semper ipsum sit amet velit. Suspendisse
id sem  
\> consectetuer libero luctus adipiscing.  
  
Itemized or unordered lists (`ul`):  
- This is the first list item.  
- This is the second list item.  
  
Enumerated or ordered Lists (`ol`):  
1. This is the first list item.  
2. This is the second list item.  
  
Maybe an equation here?  
  
See <http://www.google.com/> for more information…

### Spaces

Using non-breaking spaces.

Insert the Unicode character `00A0` to add a non-breaking space. FIXME
Or add/use an Org entity?

## Mathematical formulae

You can embed LaTeX math formatting in Org mode files using the
following syntax:

- For **inline math** expressions, use `\(...\)`: $`x^2`$ or $`1 < 2`$.

  It's *not* advised to use the constructs `$...$` (both for Org and
  MathJax).

- Centered display equation (the *Euler theorem*):

  ``` math
   \int_0^\infty e^{-x^2} dx = {{\sqrt{\pi}} \over {2}}
   
  ```

  The use of `\[...\]` is for mathematical expressions which you want to
  make **stand out, on their own lines**.

  LaTeX allows to inline such `\[...\]` constructs (*quadratic
  formula*):
  ``` math
   \frac{-b \pm \sqrt{b^2 - 4 a c}}{2a} 
  ```

  **Double dollar signs (`$$`) should not be used**.

- The *sinus theorem* can then be written as the equation:

- See Equation <span class="spurious-link"
  target="the-first">*the-first*</span>,

  Only captioned equations are numbered

- Other alternative: use \begin{equation\*} or \begin{displaymath} (=
  the verbose form of the `\[...\]` construct). M-q does not fill those.

Differently from \$…\$ and $`...`$, an equation environment produces a
**numbered** equation to which you can add a label and reference the
equation by (label) name in other parts of the text. This is not
possibly with unnumbered math environments (\$\$, …).

## Special characters

Some of the widely used special characters (converted from text
characters to their typographically correct entitites):

### Accents

À Á

### Punctuation

Dash: – —

Marks: ¡ ¿

Quotations: « »

Miscellaneous: ¶ ª

### Commercial symbols

Property marks: © ®

Currency: ¢ ¥ £

### Greek characters

The Greek letters α, β, and γ are used to denote angles.

### Math characters

Science: ± ÷

Arrows: → → ← ↔ ⇒ ⇐ ⇔

Function names: arccos  cos 

Signs and symbols: • ☆

### Misc

Suits: ♣ ♠

## Comments

It's possible to add comments in the document.

## Tables

You can create tables with an optional header row (by using an
horizontal line of dashes to separate it from the rest of the table).

| Header 1    | Header 2      | Header 3 |
|-------------|---------------|----------|
| Top left    | Top middle    |          |
|             |               | Right    |
| Bottom left | Bottom middle |          |

An example of table

Columns are automatically aligned:

- Number-rich columns to the right, and
- String-rich columns to the left.

If you want to override the automatic alignment, use `<r>`, `<c>` or
`<l>`.

|              |              |              |
|-------------:|:------------:|:-------------|
|            1 |      2       | 3            |
|        right |    center    | left         |
| xxxxxxxxxxxx | xxxxxxxxxxxx | xxxxxxxxxxxx |

Table with alignment

Placement:

|     |     |
|-----|-----|
| a   | b   |
| 1   | 2   |

XXX Different from the following:

|     |     |
|-----|-----|
| a   | b   |
| 1   | 2   |

### Align tables on the page

Here is a table on the left side:

| a   | b   | c   |
|-----|-----|-----|
| 1   | 2   | 3   |
| 4   | 5   | 6   |

The noindent just gets rid of the indentation of the first line of a
paragraph which in this case is the table. The hfill adds infinite
stretch after the table, so it pushes the table to the left.

Here is a centered table:

| a   | b   | c   |
|-----|-----|-----|
| 1   | 2   | 3   |
| 4   | 5   | 6   |

And here's a table on the right side:

| a   | b   | c   |
|-----|-----|-----|
| 1   | 2   | 3   |
| 4   | 5   | 6   |

Here the hfill adds infinite stretch before the table, so it pushes the
table to the right.

## Images, video and audio

### Images

You can insert **image** files of different **formats** to a page:

|      | HTML                         | PDF |
|------|------------------------------|-----|
| gif  | yes                          |     |
| jpeg | yes                          |     |
| png  | yes                          |     |
| bmp  | (depends on browser support) |     |

In-line picture:

<figure>
<img src="../../images/org-mode-unicorn.png" />
<figcaption>Org mode logo</figcaption>
</figure>

Direct link to just the [Unicorn picture file](org-mode-unicorn.png).

XXX Available HTML image tags include:

- align
- border
- bordercolor
- hspace
- vspace
- width
- height
- title
- alt

Place images side by side: XXX

### Video

Videos can't be added directly but you can add an image with a link to
the video like this:

[<http://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID_HERE>](http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg)

### Sounds

## Special text boxes

Simple box ("inline task"): XXX

### Example

You can have `example` blocks.

Find entries with an **exact phrase** – To do this, put the phrase in
quotes:

``` example
"hd ready"
```

You can create several other boxes (`info`, `tip`, `note` or `warning`)
which all have a different default image.

### Info

An info box is displayed as follows:

<div class="info">

**Info example**  
Did you know…

</div>

### Tip

A tip box is displayed as follows:

> [!TIP]
> **Tip example**  
> Try doing it this way…

### Note

A note box is displayed as follows:

> [!NOTE]
> **Note example**  
> This is a useful note…

### Warning

A warning box is displayed as follows:

> [!WARNING]
> **Warning example**  
> Be careful! Check that you have…

## Links

### Anchors

Links generally point to an headline.

They can also point to a link anchor
<span id="name-of-anchor-here"></span>in the current document or in
another document.

### Hyperlinks

This document is available in [plain text](example.txt),
[HTML](example.html) and [PDF](example.pdf).

The links are delimited by `[square brackets]`.

#### Internal links

See:

- chapter [Links](#links)
- section [Anchors](id:0d2b0cb2-116c-4a61-a076-4c641faf4346)
- [target in the document](#name-of-anchor-here)

#### External links

See the [Org mode Web site](http://orgmode.org/).

[Mailto link](mailto:concat.fni.at-sign.pirilampo.org)

# Org miscellaneous

## Dates

Timestamps: \[2014-01-16 Thu\] and \<2014-01-16 Thu\>.

## <span class="done DONE">DONE</span> \[#A\] Buy GTD book <span class="tag" tag-name="online"><span class="smallcaps">online</span></span>

By default, `DONE` actions will be collapsed.

Note that I should probably implement that default behavior only for
`ARCHIVE`'d items.

## <span class="todo TODO">TODO</span> \[#A\] Read GTD book

**SCHEDULED:** *\<2014-09-11 Thu\>*

By default, **all** (active) entries will be expanded at page load, so
that their contents is visible.

That can be changed by adding such a line (into your Org document):

``` org
#+HTML_HEAD: <script> var HS_STARTUP_FOLDED = true; </script>
```

## <span class="todo TODO">TODO</span> \[#B\] Apply GTD methodoloy

**DEADLINE:** *\<2014-12-01 Mon\>*

This section will be collapsed when loading the page because the entry
has the value `hsCollapsed` for the property `:HTML_CONTAINER_CLASS:`.

Powerful, no?

## Some note <span class="tag" tag-name="computer"><span class="smallcaps">computer</span></span> <span class="tag" tag-name="write"><span class="smallcaps">write</span></span>

You can add tags to any entry, and hightlight all entries having some
specific tag by clicking on the buttons made accessible to you in the
"Dashboard".

## Weekly review <span class="tag" tag-name="computer"><span class="smallcaps">computer</span></span>

Now, you can even make your weekly review in the HTML export… Press the
`r` key to start entering the "review mode" where all but one active
entry are collapsed, so that you can really focus on one item at a time!

# Org macros

<span style="color: blue"> This text is colored in blue.</span>

<span style="color: red"> This other text is in red.</span>

Find more macros on [GitHub](https://github.com/fniessen/org-macros).

# BigBlow addons

The string `fixme` (in **upper case**) gets replaced by a "Fix Me!"
image:

FIXME Delete this…

# Footnotes

[^1]: Extensively used in large documents.

[^2]: Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
    ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
    aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
    culpa qui officia deserunt mollit anim id est laborum.
