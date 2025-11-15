int global_counter = 0;
void process_data(int a, int b, int c, int d, int e) {
  int local_sum = a + b + c + d + e;
  if (local_sum >= 100) {
    global_counter = global_counter + 1;
  } else {
    global_counter = global_counter - 1;
  }
  while (global_counter < 5) {
    global_counter = global_counter + 2;
  }
}
int main(void) {
  process_data(10, 20, 30, 5, 8);
  printf("%d\n", global_counter);
}