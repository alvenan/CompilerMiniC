int gx, gy;
char gc;

int f(int a, b) { return a + b; }
int idc(char c1, c2) { return 0; }

int main() {
    int x, y;
    char c, d;

    x = 1;
    y = 2;
    c = 'a';
    d = 'b';

    x += y;
    x = x + 3;

    while (x <= 10) {
        if (x >= 5)
            break;
        else
            x = x + 1;
    }

    gy = f(x, y);
    gc = 'z';
    idc(c, d);

    return gy;
}