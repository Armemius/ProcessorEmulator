.section devices
dev0:
        byte 0x81
        addr null
        byte 0x10
        addr buffer_0
dev1:
        byte 0x81
        addr null
        byte 0x10
        addr buffer_0

.section data
buffer_0:
        str "Hello, World!"
        byte 0x0

.section text
start:
    halt
