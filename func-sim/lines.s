.ORG 0xC000
_ROM:
    mov $63, r2
    mov $0xFC00, r0
_display_loop:
    mov r2, (r0)
    dec r2
    bne _display_loop
    halt
