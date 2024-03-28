#include <stdio.h>
#include <unistd.h>
#include "com_jni_HelloJNI.h"

JNIEXPORT void JNICALL Java_com_jni_HelloJNI_printHello(JNIEnv *env, jobject obj, jstring message) {
    const char* cstring = (*env)->GetStringUTFChars(env, message, NULL);
    fprintf(stderr, "%s\n", cstring);
    (*env)->ReleaseStringUTFChars(env, message, cstring);
    return;
}
