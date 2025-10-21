int g1, g2, g3;

int add(int x, y) {
    int z;
    z = x + y;
    return z;
}

int ping() { ; return 42; }

int noop() {
    int a;
    a = 0;
    return;
}

int main() {
    int a, b, c;
    a = 1; b = 2; c = 3;
    a += b;
    b -= c;
    c *= a;
    a /= 2;
    b %= 3;

    ;

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

    return g1;
}