printintinstr = """
print:
    mov     r9, -3689348814741910323
    sub     rsp, 40
    mov     BYTE [rsp+31], 10
    lea     rcx, [rsp+30]
.L0:
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
    ja      .L0
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
    mov rax, 60       
    mov rdi, {}        
    syscall
    ; --------------          
"""
textinstr = """ ; text section
section .txt
    global _start
"""
startinstr = """

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
assigninstr = """; assignment
    pop r10 
    mov  [{}], r10  
"""
getvarinstr = """; get variable
    mov r10, [{}]
    push r10
"""
callprintinstr = """; call print
    pop rdi
    call print
"""
relationalequalityinstr = """; relational comparison
   xor rdi, rdi
   mov r10 ,1
   pop rax
   pop rcx
   cmp rcx, rax
   {} rdi, r10
   push rdi
"""
logicalistr = """; logical instr
    pop rax
    pop rcx
    test rax, rax
    setne al
    test rcx, rcx
    setne cl
    {} al, cl
    movzx eax, al
    push rax
"""
preblockinstr = """; pre block stack instr
    push rbp          ; Save the old base pointer
    mov rbp, rsp      ; Set the new base pointer
"""
blockconditioninstr = """ ;block condition check
    pop rax
    cmp rax, 1
"""
jneinstr = """;jne
    jne {}
"""
jmpinstr = """  jmp {};jmp 
"""
postblockconditioninstr ="""; post stack block
    mov rsp, rbp      ; Restore the old base pointer
    pop rbp 
"""
# pushinstr ="""; push instr
#     mov rsp, rbp      ; push variable
# """
localvarinstr = """ ; get local variable
    push qword [rbp{}]
"""
changestackvarinstr = """ ; change stack var
    pop rax
    mov [rbp{}],  rax
"""
