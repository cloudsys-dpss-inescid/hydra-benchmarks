.PHONY: all clean

CC := gcc
OBJ_DIR := build/obj
BIN_DIR := build/bin
CFLAGS := -g -Wall

all: $(BIN_DIR)/test_seccomp

# Executables
$(BIN_DIR)/test_seccomp: $(OBJ_DIR)/test_seccomp.o $(OBJ_DIR)/seccomp.o
	$(CC) $(CFLAGS) -o $@ $^ -pthread

# Object Files
$(OBJ_DIR)/test_seccomp.o: seccomp/test_seccomp.c
	$(CC) $(CFLAGS) -Iutils -c $< -o $@

$(OBJ_DIR)/seccomp.o: utils/seccomp.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(BIN_DIR)/* $(OBJ_DIR)/*