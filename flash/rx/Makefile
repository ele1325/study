# Define the compiler and the flags
CC = gcc
CFLAGS = -Wall -Wextra
DEPFLAGS = -MMD -MP

# Default parallel jobs to 16 if not specified
ifneq ($(filter -j%,$(MAKEFLAGS)),)
    # Do nothing, MAKEFLAGS already contains -j option
else
    MAKEFLAGS += -j16
endif

LDLIBS += -lws2_32

# Find all directories containing .h files
INCLUDE_DIRS := $(shell find . -type f -name "*.h" -exec dirname {} \; | sort | uniq)

# Convert directories to -I flags for the compiler
INC_FLAGS := $(addprefix -I, $(INCLUDE_DIRS))

# Define the source files by recursively finding all .c files
SRCS := $(shell find . -type f -name "*.c")

# Define the build directory for object files and dependency files
BUILD_DIR = .build

# Create corresponding .o file paths in the build directory
OBJS := $(SRCS:%.c=$(BUILD_DIR)/%.o)

# Define the dependency files
DEPS := $(OBJS:.o=.d)

# Define the output executable
TARGET = main

# The default target, it depends on the executable
all: $(TARGET)

# Rule to build the executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(INC_FLAGS) -o $@ $(OBJS) $(LDLIBS)

# Rule to build object files from source files and generate dependency files
$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INC_FLAGS) $(DEPFLAGS) -c $< -o $@

# Include the dependency files
-include $(DEPS)

# Run the program
run: $(TARGET)
	./$(TARGET)

# Clean up the generated files
clean:
	rm -rf $(BUILD_DIR) $(TARGET)

# PHONY targets
.PHONY: all clean run
