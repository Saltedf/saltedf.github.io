.intel_syntax noprefix
.globl main
main: 
  push 1
  push 3
  pop rdi
  pop rax
  cmp rdi, rax
  setle al
  movzb rax,al
  push rax
  pop rax
  ret

