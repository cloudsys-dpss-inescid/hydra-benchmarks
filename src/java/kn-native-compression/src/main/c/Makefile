.PHONY: all clean

CFLAGS = -Wall -g -fPIC -shared -I$(DEF_JAVA_HOME)/include -I$(DEF_JAVA_HOME)/include/linux -I/usr/include/
RESOURCES = ../resources

all:
	gcc $(CFLAGS) -o $(RESOURCES)/native-image/libzip-jni.so CloudFunctionApplication.c -lz

clean:
	rm -f $(RESOURCES)/native-image/libzip-jni.so
