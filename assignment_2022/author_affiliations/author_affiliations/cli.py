import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Repl this message by putting your code into "
          "author_affiliations.cli.main")
    return 0

if __name__ == "__main__":
    sys.exit(main())
