.ORG 0xC000
_ROM:
	mov $0x4000, r0         // adjust VRAM
	mov $0xFC00, r6         // adjust stack
	mov $_hello_world, r5 
	jsr r5, $_PRINT         // call print()
	mov $_sample_text, r5 
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
	cmpb $0x0D, r1
	beq _SYNC
	ash $3, r1
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	mov (r1)+, (r0)+
	br _LOOP
_EXIT:
	rts r5
_NEWLINE:
	ash $-9, r0
	inc r0
	ash $9, r0
	br _LOOP
_SYNC:
	mov $0xFC00, r3
	mov $0, (r3)
	br _LOOP

_hello_world:
	.ASCII "\n Hello World!\n\r\0"

_sample_text:
	.ASCII "                \n"
	.ASCII " Hello, PDP-11!\n"
	.ASCII "\n\n "
	.ASCII "You can choose whether to use cache or not.\n"
	.ASCII " \xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD\xCD"
	.ASCII "\n\"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\""
	.ASCII "\r\0"
