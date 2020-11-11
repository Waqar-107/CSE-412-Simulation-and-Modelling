/*
integration of sinX in the range (0, pi / 4)
integration(sinX) = -cosX + c
*/

#include<stdio.h>
#include<math.h>
#include<stdlib.h>

#define pi 3.1416

double RandomRange( double min, double max )
{
    double scale = rand() / (double) RAND_MAX; /* [0, 1.0] */
    return min + scale * ( max - min );      /* [min, max] */
}

int main()
{
    int i, j, k;
    int n, m;

    srand(time(NULL));

    double analytic_result = -(cos(pi / 4) - cos(0));
    printf("analytic result: %lf\n", analytic_result);

    int arr[] = {100, 1000, 5000,  7000, 10000};
    double ans;
    double a = 0, b = pi / 4;

    for(k = 0; k < 5; k++)
    {
        n = arr[k];
        ans = 0.0;

        for(i = 0; i < n; i++)
            ans += sin(RandomRange(a, b));

        ans /= n;
        ans *= (b - a);

        printf("%lf ", ans);
    }

    return 0;
}
