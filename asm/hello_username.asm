.section devices
dev0:
        byte 0x81
        addr null
        byte 0xFF
        addr buffer_1
dev1:
        byte 0x01
        addr null
        byte 0xFF
        addr buffer_0

.section data
a:
        res 4
b:
        res 4
result:
        res 4

ch:
    res 4

it:
    byte 0x0, 0x0, 0x0, 0x0

jt:
    byte 0x0, 0x0, 0x0, 0x7

char:
    res 4

buffer_0:
    char 'H', 'e', 'l', 'l'
    char 'o', ',', ' '
    res 0xFF
buffer_1:
    res 0xFF

.section text

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

ld_it:
    push it
    ld
    swap
    pop
    swap
    ret

ld_ch:
    push ch
    ld
    swap
    pop
    swap
    ret

ld_jt:
    push jt
    ld
    swap
    pop
    swap
    ret

st_jt:
    swap
    push jt
    swap
    st
    pop
    ret

st_ch:
    swap
    push ch
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

load_char:
    call ld_it
    call st_a
    push 4
    call st_b
    call mod_ab ; res = it % 4

    push 4
    call ld_it
    div ; tos = it / 4
    push buffer_1
    add ; tos = buffer_1 + it / 4
    ld
    swap
    pop ; tos = buffer_1[it / 4]

    call ld_result
    push 4
    sub

load_char_loop:
    dec
    push 0
    cmp
    pop
    jz load_char_end
    swap
    shr shr shr shr shr shr shr shr
    swap

    jmp load_char_loop
load_char_end:
    pop

    push 0xFF
    and

    ror ror ror ror ror ror ror ror
    call st_ch

    call ld_it
    inc
    call st_it

    ret

save_char:
    call ld_jt
    call st_a
    push 4
    call st_b
    call mod_ab ; res = it % 4

    call ld_ch

    call ld_result

save_char_loop:
    push 0
    cmp
    pop
    jz save_char_end
    swap
    shr shr shr shr shr shr shr shr
    swap
    dec
    jmp save_char_loop
save_char_end:
    pop

    push 4
    call ld_jt
    div ; tos = jt / 4
    push buffer_0
    add ; tos = buffer_0 + it / 4
    ld
    swap
    pop
    or

    push 4
    call ld_jt
    div ; tos = jt / 4
    push buffer_0
    add ; tos = buffer_0 + it / 4
    swap
    st
    pop

    call ld_jt
    inc
    call st_jt

    ret

start:
    unset dev0
main_loop:
    call load_char
    call ld_ch
    push 0x0
    cmp
    pop
    pop
    jz main_end
    call save_char
    jmp main_loop


main_end:
    push 0x21
    ror ror ror ror ror ror ror ror
    call st_ch
    call save_char
    set dev1
    halt
