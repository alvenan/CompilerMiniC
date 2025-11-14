int g;

void setg(int x) {
    g = x;
}

int main() {
    int a;
    a = 10;
    setg(a);
    a = 20;

    return g;
}
