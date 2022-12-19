#ifndef __LIBHELLOWORLD_H
#define __LIBHELLOWORLD_H

#include <graal_isolate_dynamic.h>


#if defined(__cplusplus)
extern "C" {
#endif

typedef void (*vmLocatorSymbol_fn_t)(graal_isolatethread_t* thread);

typedef void (*dumpImageMethods_fn_t)();

#if defined(__cplusplus)
}
#endif
#endif
