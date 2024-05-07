#include "MatrixMultiplication.h"
#include <stdio.h>
#include <stdlib.h>

#define ROWS 5
#define COLS 5

void matrixGenerator(int **matrix){
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            matrix[i][j] = 10000; 
        }
    }
}

int** allocateMatrix() {
    int **matrix = (int **)malloc(ROWS * sizeof(int *));
    for (int i = 0; i < ROWS; i++) {
        matrix[i] = (int *)malloc(COLS * sizeof(int));
    }
    return matrix;
}


JNIEXPORT void JNICALL Java_com_jni_MatrixMultiplication_multiply(JNIEnv *env, jobject object) {
	int** matrix1 = allocateMatrix();
	int** matrix2 = allocateMatrix();
    int** result = allocateMatrix();
	
	matrixGenerator(matrix1);
	matrixGenerator(matrix2);

    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            result[i][j] = 0;
            for (int k = 0; k < ROWS; k++) {
                result[i][j] += matrix1[i][k] * matrix2[k][j];
            }
        }
    }

    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            fprintf(stderr, "%d ", result[i][j]);
        }
        fprintf(stderr, "\n");
    }
}
