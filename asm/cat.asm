.section devices
dev0:
        byte 0x81
        addr null
        byte 0xFF
        addr buffer_0
dev1:
        byte 0x01
        addr null
        byte 0xFF
        addr buffer_0

.section data
buffer_0:
        res 0xFF

.section text
start:
    unset dev0
    check dev0
    jz end
    set dev1
    jmp start

end:
    halt
