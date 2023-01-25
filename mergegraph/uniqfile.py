import sys

# Given a text file, this removes duplicate lines.

def readFile(filename):
    result = []
    with open(filename) as f:
        for line in f:
            result.append(line)
    return result

if __name__ == "__main__":
    # Args: [1] is the filename to process.

    lines = readFile(sys.argv[1])
    for line in sorted(set(lines)):
        print(line.strip())
