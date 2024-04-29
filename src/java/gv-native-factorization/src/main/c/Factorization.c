#include "com_jni_Factorization.h"
#include <stdio.h>
#include <sys/mman.h>

#define MAX_FACTORS 5


JNIEXPORT void JNICALL Java_com_jni_Factorization_computeFactors(JNIEnv *env, jobject object) {
    //int* num_factors = (int*)malloc(sizeof(int)*MAX_FACTORS);
    //fprintf(stderr, "num_factors Pointer -> %p\n", num_factors);
    void *mapped = mmap(NULL, 256, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    //fprintf(stderr, "mmap Pointer -> %p\n", addr);

    /*
    int count = 0;
    int number = 1000000;
    
    for (int i = 1; i <= number; i++) {
        if (count == MAX_FACTORS)
          break;
        if((number % i) == 0){
            //num_factors[count++] = i;
            fprintf(stderr, "%d -> Factor number %d \n", i, ++count);
        }
    }
    */

    /*
    for(int i = 0;i < count;i++){
        fprintf(stderr, "%d -> Factor number %d \n", num_factors[i], i);
    }
    */
}
