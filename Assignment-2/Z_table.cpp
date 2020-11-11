#include<iostream>
#include<cmath>
#include<ctime>
#include<cstdlib>

#define pi 3.1416

using namespace std;

// selects a random between lo and hi
float RandomRange( float lo, float hi )
{
    float scale = (float)rand() / (float) RAND_MAX;
    return lo + scale * ( hi - lo );
}

// the g(X)
float integral(float u)
{
    float down = 1 / (sqrt(2 * pi) * u);
    float p = (log(u) * log(u)) / -2;

    return down * exp(p);
}

int main()
{
    int i, j, k;
    int n, m;

    float ans, a, b, x, z;
    float col, row;

    row = 0.0;
    n = 1000;
    int seed = 118;

    cout << "         0.01    0.02    0.03    0.04    0.05    0.06    0.07    0.08    0.09" << endl;
    while(row <= 3.0)
    {
        cout.precision(1);
        cout << fixed << row << "    ";

        col = 0.01;
        while(col <= 0.09)
        {
            ans = 0.0;
            z = row + col;

            a = 0;
            b = exp(z);

            // for every z-value, reset the random number generator
            srand(seed);

            for(i = 0; i < n; i++)
            {
                x = integral(RandomRange(a, b));
                ans += x;
            }

            ans /= n;
            ans *= (b - a);

            cout.precision(4);
            cout << fixed << ans << "  ";
            col += 0.01;
        }

        cout << endl;
        row += 0.1;
    }


    return 0;
}
