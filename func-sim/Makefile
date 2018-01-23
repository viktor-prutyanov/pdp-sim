AS=${BINUTILS}/gas/as-new
OBJCOPY=${BINUTILS}/binutils/objcopy

all: sample.bin

%.bin: %.s
	$(AS) $^ -o $^.o
	$(OBJCOPY) -O binary $^.o $@.huge
	dd if=$@.huge of=$@ bs=1K skip=48
	rm -f $^.o $@.huge

.PHONY: clean

clean:
	rm -f sample.bin
