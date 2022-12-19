#ifndef __LIBHELLOWORLD_H
#define __LIBHELLOWORLD_H

#include <graal_isolate.h>


#if defined(__cplusplus)
extern "C" {
#endif

void vmLocatorSymbol(graal_isolatethread_t* thread);

void dumpImageMethods();

#if defined(__cplusplus)
}
#endif
#endif
