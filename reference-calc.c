#include <stdio.h>
#include <stdlib.h>

float performOperation(float num1, float num2, char operator);

int main(int argc, char* argv[]) {

    if (argc < 4) {
        printf("Usage: ./calc operand1 operator operand2\n");

        return 1;
    }

    float num1 = atof(argv[1]);
    char operator = argv[2][0];
    float num2 = atof(argv[3]);

    float result = performOperation(num1, num2, operator);

    printf("%f\n", result);

    return 0;
}

float performOperation(float num1, float num2, char operator) {
    switch (operator) {
        case '+':
            return num1 + num2;
        case '-':
            return num1 - num2;
        case '*':
            return num1 * num2;
        case '/':
            return num1 / num2;
        default:
            printf("Error: Invalid operand\n");
            exit(1);
    }
}
