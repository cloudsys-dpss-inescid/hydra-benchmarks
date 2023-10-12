#include <null.h>
#include <unistd.h>
#include <stdlib.h>
#include "com.hello_jni.HelloJNI.h"

// Erim includes
#include <erim.h>
#include <common.h>

static __thread char* regular = NULL; // thread regular stack
static __thread int hasFilter = 0; // seccomp filter is applied

/* Function declaration */
void wrapper(int domain, JNIEnv *env, jobject obj);

JNIEXPORT void JNICALL Java_com.hello_jni.HelloJNI_printHelloCallGate(JNIEnv *env, jobject obj) {
	lock();

	/* Get available domain */
	SNI_DBM("[s]: Getting available domain...");
	int domain = find_app_domain("libc866170bebd034d55b0d664db400105e6");
	while (domain == -1) {
		//FIXME: active waiting
		sleep(1);
		domain = find_empty_domain();
	}

	/* Handle native library permissions */
	SNI_DBM("[s]: Handling permissions for domain %d...", domain);
	update_supervisor_app(domain, "libc866170bebd034d55b0d664db400105e6");
	signal_perms(domain);

	/* Wait for all permissions to be set */
	wait_set(domain);
	SNI_DBM("[s]: permissions are all set, continuing...");

	unlock();

	/* Switch to new stack */
	SNI_DBM("[s]: switching to new stack...");
	ERIM_SWITCH_STACK(ERIM_DOMAIN_STACK_LOC(domain), regular);
	wrapper(domain, env, obj);
	ERIM_SWITCH_BACK(regular);

	/* Notify supervisor of the app's completion */
	SNI_DBM("[s]: application terminated!");
	update_supervisor_status(domain);
}


void wrapper(int domain, JNIEnv *env, jobject obj) {
	void (*native_method)(JNIEnv*, jobject) = dlsym(RTLD_DEFAULT, "Java_com.hello_jni.HelloJNI_printHello");
	if (native_method == NULL) {
		fprintf(stderr, "Failed to find the symbol: Java_com.hello_jni.HelloJNI_printHello\n");
		exit(EXIT_FAILURE);
	}

	/* Install seccomp filter */
	SNI_DBM("[s]: installing filter...");
	if (!hasFilter) {
		install_notify_filter(domain);
		hasFilter = 1;
	}
	signal_filter(domain);

	wait_handler(domain);
	SNI_DBM("[s]: handler's ready, changing domain...");
	__wrpkrumem(ERIM_DOMAIN(domain));
	native_method(env, obj);
	__wrpkru(0);
}
