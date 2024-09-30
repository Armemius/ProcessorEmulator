.section devices
dev0:
        byte 0x81
        addr null
        byte 0x4
        addr buffer_0
dev2:
        byte 0x01
        addr null
        byte 0x4
        addr buffer_0

.section data
buffer_0:
        res 4
it:
        res 4
a:
        res 4
b:
        res 4
temp:
        res 4
result:
        res 4

.section text
ld_a:
    push a
    ld
    swap
    pop
    swap
    ret

ld_b:
    push b
    ld
    swap
    pop
    swap
    ret

ld_result:
    push result
    ld
    swap
    pop
    swap
    ret

ld_temp:
    push temp
    ld
    swap
    pop
    swap
    ret

ld_buffer:
    push buffer_0
    ld
    swap
    pop
    swap
    ret

ld_it:
    push it
    ld
    swap
    pop
    swap
    ret

st_a:
    swap
    push a
    swap
    st
    pop
    ret

st_b:
    swap
    push b
    swap
    st
    pop
    ret

st_result:
    swap
    push result
    swap
    st
    pop
    ret

st_temp:
    swap
    push temp
    swap
    st
    pop
    ret

st_buffer:
    swap
    push buffer_0
    swap
    st
    pop
    ret

st_it:
    swap
    push it
    swap
    st
    pop
    ret

mod_ab: ; res = a % b
    call ld_b
    call ld_a
    div
    call st_result
    call ld_result
    call ld_b
    mul
    call ld_a
    sub
    call st_result
    ret

gcd_ab:
    call ld_a
    push 0
    cmp
    pop
    pop
    je gcd_end

    call ld_b
    push 0
    cmp
    pop
    pop
    je gcd_end

    call ld_b
    call ld_a
    cmp
    jg gcd_b_less

gcd_a_less:
    call st_b
    call st_a

    call mod_ab

    call ld_result
    call st_a

    jmp gcd_ab

gcd_b_less:

    call st_a
    call st_b

    call mod_ab

    call ld_result
    call st_a

    jmp gcd_ab

gcd_end:
    call ld_a
    call ld_b
    add
    call st_result
    ret

lcm_ab:
    call ld_b
    call ld_a
    call gcd_ab
    call ld_result
    swap
    div
    mul
    call st_result
    ret

start:
    push 1
    call st_buffer
    push 2
    call st_it

loop:
    call ld_buffer
    call st_a
    call ld_it
    call st_b
    call lcm_ab
    call ld_result
    call st_buffer

    push 20
    call ld_it
    cmp
    pop
    pop
    jz end

    call ld_it
    inc
    call st_it
    jmp loop

end:
    set dev2
    halt
