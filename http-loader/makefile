CC = gcc
CFLAGS = -g -Wall -Wextra -pthread
LDFLAGS = -lresolv -lm  

SRCS = http_post.c
OBJS = $(SRCS:.c=.o)
TARGET = http_post

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	$(RM) $(OBJS) $(TARGET)


CC = gcc
CFLAGS = -g -Wall -Wextra -pthread
LDFLAGS = -lresolv -lm  

SRCS = http_post.c
OBJS = $(SRCS:.c=.o)
TARGET = http_post

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	$(RM) $(OBJS) $(TARGET)
