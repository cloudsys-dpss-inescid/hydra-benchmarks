#include <stdio.h>
#include <unistd.h>
#include "com_jni_HelloJNI.h"

JNIEXPORT void JNICALL Java_com_jni_HelloJNI_printHello15(JNIEnv *env, jobject obj) {
    fprintf(stderr, "Hello World 15!\n");
    return;
}
