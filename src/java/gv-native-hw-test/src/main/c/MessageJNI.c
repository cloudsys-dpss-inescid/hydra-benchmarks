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

static __thread char* regular = NULL; // thread regular stack
static __thread int fd = 0; // seccomp filter fd

/* Function declaration */
void wrapper(JNIEnv *env, jobject obj, jstring arg0);


JNIEXPORT void JNICALL Java_com_jni_MessageJNI_printMessage(JNIEnv *env, jobject obj, jstring string) {
    const char* cname = (*env)->GetStringUTFChars(env, string, NULL);
    fprintf(stdout, "%s\n", cname);
    (*env)->ReleaseStringUTFChars(env, string, cname);
    return;
}


JNIEXPORT void JNICALL Java_com_jni_MessageJNI_printMessageCallGate(JNIEnv *env, jobject obj, jstring arg0) {
	/* Get available domain */
	acquire_domain("nativemsg", &fd);
	if (domain == -1) {
		return;
	}

	/* Switch to new stack */
	ERIM_SWITCH_STACK(ERIM_DOMAIN_STACK_LOC(domain), regular);
	wrapper(env, obj, arg0);
	ERIM_SWITCH_BACK(regular);

	reset_env("nativemsg", 0);
}


void wrapper(JNIEnv *env, jobject obj, jstring arg0) {
	if ((*env)->GetStringUTFChars != Faastion_GetStringUTFChars) {
		init_jni_wrapper(env);
	}

	__wrpkrumem(ERIM_DOMAIN(domain));
	Java_com_jni_MessageJNI_printMessage(env, obj, arg0);
	__wrpkru(0);
}
