.ORG 0xC000
_ROM:
	mov $0xFC00, r6
	mov $0x1234, r5
	jsr r5, $_FUNC
	halt
_FUNC:
	mov $1, r1
	rts	r5
