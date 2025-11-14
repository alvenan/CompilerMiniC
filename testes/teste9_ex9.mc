int main() {
    int i, sum;
    i = 0;
    sum = 0;

    while (i < 10) {
        i = i + 1;
        if (i == 3)
            continue;
        if (i == 7)
            break;
        sum = sum + i;
    }

    return sum;
}
