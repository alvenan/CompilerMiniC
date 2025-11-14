int g1, g2;
char gc;

int add(int x, y) { int z; z = x + y; return z; }
int echoChar(char d, e) { return 0; }
int ping() { ; return 42; }
int noop() { return; }

int main() {
    int a, b, c;
    char d, e;

    a = 1; b = 2; c = 3;
    d = 'x'; e = 'y';

    a += b;
    b -= c;
    c *= a;
    a /= 2;
    b %= 3;

    if (a == b)
        ;
    else {
        a = a + 1;
    }

    if (a != b) {
        ++a;
    } else {
        --b;
    }

    while (a < b) {
        a = a + 1;
        if (a >= b)
            break;
        else
            continue;
    }

    if (a <= b) { a = a - 1; }

    a = (a + b) * c / (a % 2 + 1);
    g1 = add(a, (b + c) * (a - 1));
    echoChar(d, e);
    gc = 'z';

    g2 = ping();
    noop();

    return g1;
}