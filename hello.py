:wq
iame: Code Style Check

on: [push, pull_request]

jobs:
  clang-format:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install clang-format
        run: sudo apt-get install -y clang-format

      - name: Run clang-format style check
        run: |
          find ./src ./examples -regex '.*\.\(cpp\|cc\|c\|h\|hpp\)' \
            -exec clang-format --dry-run --Werror {} +

