import sys
import matplotlib.pyplot as plt


display_words = 20
total = 1947152902
def calculate_freq(filename):
    ref_sum = 0
    freqs = {}
    with open(filename, encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            word, count = text.split()
            if word not in freqs:
                freqs[word] = int(count) / total
    word = []
    frequency = []
    for key, val in freqs.items():
        if key == None or val == None:
            print('NONE ENCOUNTERED')
            print(key)
            print(val)
        word.append(key)
        frequency.append(val)

    write_word_freq(freqs)

    plt.bar(word[:20], frequency[:20])
    plt.title('Word frequency from all the words on wikipedia.')
    plt.xlabel('Word')
    plt.ylabel('Word Frequency')
    plt.show()

def write_word_freq(freqs):
    lines = []
    f = open('word_freq.txt', 'w', encoding="utf-8")
    for key, val in freqs.items():
        out = '{} {}\n'.format(key, val)
        lines.append(out)
    f.writelines(lines)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please enter the name of the text file.')
        sys.exit()
    filename = sys.argv[1]
    calculate_freq(filename)