#include <memisolation.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <spawn.h>
#include <string.h>
#include <stdio.h>
#include "JNIWrapper.h"
#include "com_jni_MessageJNI.h"

// Erim includes
#include <erim.h>
#include <common.h>

JNIEXPORT void JNICALL Java_com_jni_MessageJNI_printMessageCallGate(JNIEnv *env, jobject obj, jstring string) {
    const char* cname = (*env)->GetStringUTFChars(env, string, NULL);
    fprintf(stdout, "%s\n", cname);
    (*env)->ReleaseStringUTFChars(env, string, cname);
    return;
}
