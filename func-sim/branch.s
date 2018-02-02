    inc r4
    asl r4
    asl r4
    asl r4
_loop:
    inc r0
    inc r1
    inc r2
    dec r4
    bne _loop
    halt
