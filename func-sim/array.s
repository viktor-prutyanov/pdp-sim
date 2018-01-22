_RAM:
.ORG 0x3C00
_VRAM:
.ORG 0xC000
_ROM:
    mov $4, r2
    mov $_src_array, r0
    mov $_dst_array, r1
_loop:
    mov (r0)+, (r1)+
    dec r2
    bne _loop
    halt
_src_array:
    .WORD 0x1234
    .WORD 0x5678
    .WORD 0x89AB
    .WORD 0xCDEF
_dst_array:
    .WORD 0x0000
    .WORD 0x0000
    .WORD 0x0000
    .WORD 0x0000
.ORG 0xFC00
_IO:
