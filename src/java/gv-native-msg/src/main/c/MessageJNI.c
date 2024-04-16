#include <stdio.h>
#include <unistd.h>
#include "com_jni_MessageJNI.h"

JNIEXPORT void JNICALL Java_com_jni_MessageJNI_printMessage(JNIEnv *env, jobject obj, jstring string) {
    const char* cname = (*env)->GetStringUTFChars(env, string, NULL);
    fprintf(stdout, "%s\n", cname);
    (*env)->ReleaseStringUTFChars(env, string, cname);
    return;
}
