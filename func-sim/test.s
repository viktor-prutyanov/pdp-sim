.ORG 0xC000
_ROM:
	mov $0x4000, r0         // adjust VRAM
	mov $0xFC00, r6         // adjust stack
	mov $_hello_world, r5 
	jsr r5, $_PRINT         // call print()
	halt

_PRINT:                     // print subroutine
	mov (r6), r2
_LOOP:
	movb (r2)+, r1
	tstb r1
	beq _EXIT
	cmpb $0x0A, r1
	beq _NEWLINE
	ash $3, r1
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	mov $0xFC00, r3
	mov $0, (r3)
	br _LOOP
_EXIT:
	rts r5
_NEWLINE:
	ash $-9, r0
	inc r0
	ash $9, r0
	br _LOOP

_hello_world:
	.ASCII "\n Hello World!\n\0"
