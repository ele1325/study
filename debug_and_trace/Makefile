# ------------------------------------------------------------------------------
# toolchain

CC=gcc
# ------------------------------------------------------------------------------
# function

define find
	$(foreach dir,$(1),$(foreach d,$(wildcard $(dir)/*),\
		$(call find,$(d),$(2))) $(wildcard $(dir)/$(strip $(2))))
endef

define NEWLINE

endef


# ------------------------------------------------------------------------------
# 

target = dt

source_path = . 
output_path = build

source_files = $(call find, $(source_path), *.c)
object_files = ${source_files:.c=.o}
output_files = $(addprefix $(output_path)/, $(object_files))

CFLAGS += -I. \
		  -I./global \


CFLAGS += -DDEBUG_ENABLE -g # GDB

# $(output_path)/$(target): $(output_files)

$(target): $(output_files)
	$(CC) -o $@ $^

$(output_path)/%.o: %.c
	mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@ 

run:
	./$(target)

clean:
	rm -rf $(output_path)
	rm $(target)