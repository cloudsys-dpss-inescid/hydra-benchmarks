#include <jni.h>

#ifndef _Included_com.hello_jni.HelloJNI
#define _Included_com.hello_jni.HelloJNI

#ifdef SNI_DBG
#define SNI_DBM(...) \
	do { \
	fprintf(stderr, __VA_ARGS__); \
	fprintf(stderr, "\n"); \
	} while(0)
#else // disable debug
#define SNI_DBG(...)
#endif

JNIEXPORT void JNICALL Java_com.hello_jni.HelloJNI_printHelloCallGate
	(JNIEnv *, jclass);

#endif
