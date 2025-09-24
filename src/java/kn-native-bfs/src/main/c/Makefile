.PHONY: all clean

CFLAGS = -Wall -g -fPIC -shared -I$(DEF_JAVA_HOME)/include -I$(DEF_JAVA_HOME)/include/linux -I/usr/include/
RESOURCES = ../resources

all:
	gcc $(CFLAGS) -Wl,--no-undefined -I$(IGRAPH_HOME)/include/igraph -L$(IGRAPH_HOME)/lib -o $(RESOURCES)/native-image/libbfs-jni.so CloudFunctionApplication.c -ligraph -lm -fopenmp -lstdc++	


clean:
	rm -f $(RESOURCES)/native-image/libbfs-jni.so
