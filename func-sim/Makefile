AS=${BINUTILS}/gas/as-new
OBJCOPY=${BINUTILS}/binutils/objcopy

sample.bin: sample.s
	$(AS) $^ -o sample.o
	$(OBJCOPY) -O binary sample.o $@
	rm -f sample.o

.PHONY: clean

clean:
	rm -f sample.bin
