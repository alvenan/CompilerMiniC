int g1, g2, g3;
char gc;

int add(int x, y) { int z; z = x + y; return z; }
int id(int v) { return v; }

int main() {
    int a, b, c, d, e, f;
    char ch1, ch2;

    a = 2;
    b = 3;
    c = 0;
    d = 1;
    e = 4;
    f = 0;
    ch1 = 'x';
    ch2 = 'y';

    c = 0 + 0;
    d = d * 1;
    e = 1 * e;
    f = b * 0;
    a = a / 1;
    b = b + 0;

    g1 = a + b;
    g2 = a + b;

    if (a == b) {
        c = c + 1;
    } else {
        c = c + 0;
    }

    if (a != b) {
        ++a;
    } else {
        --b;
    }

    if (a < b) {
        d = d + 1;
    }
    if (a <= b) {
        d = d + 2;
    }
    if (a > b) {
        d = d + 3;
    }
    if (a >= b) {
        d = d + 4;
    }

    while (a < b + 3) {
        a += 1;
        if (a == b + 1)
            continue;
        if (a == b + 2)
            break;
    }

    a = (a + b) * e / (a % 2 + 1);
    g3 = add(a, (b + e) * (a - 1));

    g2 = id(g1);
    gc = 'z';

    return g3;
}

