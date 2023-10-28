printintinstr = """
print:
    mov     r9, -3689348814741910323
    sub     rsp, 40
    mov     BYTE [rsp+31], 10
    lea     rcx, [rsp+30]
.L2:
    mov     rax, rdi
    lea     r8, [rsp+32]
    mul     r9
    mov     rax, rdi
    sub     r8, rcx
    shr     rdx, 3
    lea     rsi, [rdx+rdx*4]
    add     rsi, rsi
    sub     rax, rsi
    add     eax, 48
    mov     BYTE [rcx], al
    mov     rax, rdi
    mov     rdi, rdx
    mov     rdx, rcx
    sub     rcx, 1
    cmp     rax, 9
    ja      .L2
    lea     rax, [rsp+32]
    mov     edi, 1
    sub     rdx, rax
    xor     eax, eax
    lea     rsi, [rsp+32+rdx]
    mov     rdx, r8
    mov     rax, 1
    syscall
    add     rsp, 40
    ret
"""
exitinstr = """
    ; exit section---
    ; temp
    pop rdi
    call print
    mov rax, 60       
    mov rdi, {}        
    syscall
    ; --------------          
"""
startinstr = """
global _start

_start:
"""
addinstr  = """; add instruction
    pop rdx
    pop rax
    add rax ,rdx
    push rax 
"""
numlitinstr = """; num lit
    push {}
"""
subinstr = """; sub 
    pop rdx
    pop rax
    sub rax ,rdx
    push rax 
"""
multinstr = """; mul 
    pop rdx
    pop rax
    imul rax, rdx
    push rax 
"""
divinstr = """; div
    ; xor rdx, rdx
    pop rbx
    pop rax
    cdq 
    idiv rbx
    push rax 
"""