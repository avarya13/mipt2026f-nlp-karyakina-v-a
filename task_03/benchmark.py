import os
import random
import string
import time
from collections import deque

def naive_search(text, pattern):
    n, m = len(text), len(pattern)
    res = []
    if m == 0:
        return res
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            res.append(i)
    return res

def prefix_function(s):
    n = len(s)
    p = [0] * n
    for i in range(1, n):
        k = p[i - 1]
        while k > 0 and s[i] != s[k]:
            k = p[k - 1]
        if s[i] == s[k]:
            k += 1
        p[i] = k
    return p

def kmp_search(text, pattern):
    if not pattern:
        return []
    p = prefix_function(pattern)
    m = len(pattern)
    k = 0
    res = []
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = p[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = p[k - 1]
    return res

def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z

def z_search(text, pattern):
    if not pattern:
        return []
    s = pattern + '#' + text
    z = z_function(s)
    m = len(pattern)
    res = []
    for i in range(m + 1, len(s)):
        if z[i] >= m:
            res.append(i - m - 1)
    return res

def prefix_search(text, pattern):
    if not pattern:
        return []
    s = pattern + '#' + text
    p = prefix_function(s)
    m = len(pattern)
    res = []
    for i in range(m + 1, len(s)):
        if p[i] == m:
            res.append(i - 2 * m)
    return res

def rabin_karp_search(text, pattern, base=256, mod=10**9 + 7):
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    pattern_hash = 0
    window_hash = 0
    power = 1
    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        window_hash = (window_hash * base + ord(text[i])) % mod
        if i < m - 1:
            power = (power * base) % mod
    res = []
    if pattern_hash == window_hash and text[:m] == pattern:
        res.append(0)
    for i in range(m, n):
        window_hash = (window_hash - ord(text[i - m]) * power) % mod
        window_hash = (window_hash * base + ord(text[i])) % mod
        if window_hash == pattern_hash and text[i - m + 1:i + 1] == pattern:
            res.append(i - m + 1)
    return res

def prepare_rabin_karp_multi(patterns, base=256, mod=10**9 + 7):
    by_len = {}
    for idx, pat in enumerate(patterns):
        m = len(pat)
        if m not in by_len:
            by_len[m] = {}
        h = 0
        for ch in pat:
            h = (h * base + ord(ch)) % mod
        by_len[m].setdefault(h, []).append(idx)
    return by_len

def rabin_karp_multi_search_prepared(text, patterns, by_len, base=256, mod=10**9 + 7):
    n = len(text)
    res = []
    for m, hash_dict in by_len.items():
        if m > n:
            continue
        window_hash = 0
        power = 1
        for i in range(m):
            window_hash = (window_hash * base + ord(text[i])) % mod
            if i < m - 1:
                power = (power * base) % mod
        if window_hash in hash_dict:
            for idx in hash_dict[window_hash]:
                if text[:m] == patterns[idx]:
                    res.append((0, idx))
        for i in range(m, n):
            window_hash = (window_hash - ord(text[i - m]) * power) % mod
            window_hash = (window_hash * base + ord(text[i])) % mod
            if window_hash in hash_dict:
                for idx in hash_dict[window_hash]:
                    if text[i - m + 1:i + 1] == patterns[idx]:
                        res.append((i - m + 1, idx))
    return res

class AhoCorasick:
    def __init__(self):
        self.next = [{}]
        self.fail = [0]
        self.output = [[]]

    def add_word(self, word, idx):
        node = 0
        for ch in word:
            if ch not in self.next[node]:
                self.next[node][ch] = len(self.next)
                self.next.append({})
                self.fail.append(0)
                self.output.append([])
            node = self.next[node][ch]
        self.output[node].append(idx)

    def build(self):
        q = deque()
        for ch, node in self.next[0].items():
            self.fail[node] = 0
            q.append(node)
        while q:
            v = q.popleft()
            for ch, u in self.next[v].items():
                f = self.fail[v]
                while f and ch not in self.next[f]:
                    f = self.fail[f]
                self.fail[u] = self.next[f].get(ch, 0)
                self.output[u].extend(self.output[self.fail[u]])
                q.append(u)

    def search(self, text, patterns):
        node = 0
        res = []
        for i, ch in enumerate(text):
            while node and ch not in self.next[node]:
                node = self.fail[node]
            node = self.next[node].get(ch, 0)
            for pat_idx in self.output[node]:
                start = i - len(patterns[pat_idx]) + 1
                res.append((start, pat_idx))
        return res

def generate_data(num_words=10000, num_texts=1000, seed=42):
    random.seed(seed)
    alphabet = string.ascii_lowercase + string.digits
    words = set()
    while len(words) < num_words:
        length = random.randint(3, 12)
        word = ''.join(random.choice(alphabet) for _ in range(length))
        words.add(word)
    words = list(words)

    texts = []
    for _ in range(num_texts):
        length = random.randint(500, 2000)
        text_chars = [random.choice(alphabet) for _ in range(length)]
        for _ in range(10):
            w = random.choice(words)
            pos = random.randint(0, length - len(w))
            text_chars[pos:pos + len(w)] = list(w)
        texts.append(''.join(text_chars))
    return words, texts

def save_data(words, texts, data_dir='data'):
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, 'words.txt'), 'w', encoding='utf-8') as f:
        for w in words:
            f.write(w + '\n')
    with open(os.path.join(data_dir, 'texts.txt'), 'w', encoding='utf-8') as f:
        for t in texts:
            f.write(t + '\n')

def load_data(data_dir='data'):
    words_path = os.path.join(data_dir, 'words.txt')
    texts_path = os.path.join(data_dir, 'texts.txt')
    if not (os.path.exists(words_path) and os.path.exists(texts_path)):
        return None, None
    with open(words_path, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    with open(texts_path, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    return words, texts

def benchmark_single(algo, texts, words, name):
    print(f"Running {name}...")
    start = time.perf_counter()
    total_matches = 0
    for text in texts:
        for word in words:
            matches = algo(text, word)
            total_matches += len(matches)
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.2f} sec, matches {total_matches}")
    return elapsed, total_matches

def benchmark_multi_prepared(searcher, texts, patterns, name):
    print(f"Running {name}...")
    start = time.perf_counter()
    total_matches = 0
    for text in texts:
        matches = searcher(text, patterns)
        total_matches += len(matches)
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.2f} sec, matches {total_matches}")
    return elapsed, total_matches

def write_results(results, filename='results.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for name, elapsed, matches in results:
            f.write(f"{name}: {elapsed:.2f} sec, matches {matches}\n")

if __name__ == "__main__":
    NUM_WORDS = 1000
    NUM_TEXTS = 100

    words, texts = load_data()
    if words is None:
        print("Generating data...")
        words, texts = generate_data(NUM_WORDS, NUM_TEXTS)
        save_data(words, texts)
        print(f"Generated words: {len(words)}, texts: {len(texts)}")
        print("Data saved to data/words.txt and data/texts.txt")
    else:
        print(f"Loaded words: {len(words)}, texts: {len(texts)} from data/")

    results = []

    # elapsed, matches = benchmark_single(naive_search, texts, words, "Naive")
    # results.append(("Naive", elapsed, matches))

    elapsed, matches = benchmark_single(kmp_search, texts, words, "KMP")
    results.append(("KMP", elapsed, matches))

    elapsed, matches = benchmark_single(z_search, texts, words, "Z-function")
    results.append(("Z-function", elapsed, matches))

    elapsed, matches = benchmark_single(prefix_search, texts, words, "Prefix-function")
    results.append(("Prefix-function", elapsed, matches))

    elapsed, matches = benchmark_single(rabin_karp_search, texts, words, "Rabin-Karp (single)")
    results.append(("Rabin-Karp (single)", elapsed, matches))

    print("\nPreparing Rabin-Karp (multi)...")
    by_len = prepare_rabin_karp_multi(words)
    def rk_multi_searcher(text, patterns):
        return rabin_karp_multi_search_prepared(text, patterns, by_len)
    elapsed, matches = benchmark_multi_prepared(rk_multi_searcher, texts, words, "Rabin-Karp (multi)")
    results.append(("Rabin-Karp (multi)", elapsed, matches))

    print("\nPreparing Aho-Corasick...")
    ac = AhoCorasick()
    for idx, w in enumerate(words):
        ac.add_word(w, idx)
    ac.build()
    def ac_searcher(text, patterns):
        return ac.search(text, patterns)
    elapsed, matches = benchmark_multi_prepared(ac_searcher, texts, words, "Aho-Corasick")
    results.append(("Aho-Corasick", elapsed, matches))

    write_results(results)
    print("Results saved to results.txt")