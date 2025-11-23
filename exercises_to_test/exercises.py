def is_palindrome(text: str):
    text = text.replace(" ", "").lower()
    if not text:
        return True
    if text == text[::-1]:
        return True
    else:
        return False


def fibonacci(n: int):
    if n < 0:
        return ValueError("Input should be a non-negative integer")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        fib_seq = [0, 1]
        for i in range(1, n):
            next_fib = fib_seq[-1] + fib_seq[-2]
            fib_seq.append(next_fib)
        return fib_seq[-1]


def count_vowels(text: str):
    vowels = "aeiouyAEIOUY"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count


def calculate_discount(price, discount):
    if discount < 0:
        raise ValueError("Discount must be between 0 and 1")
    if discount > 1:
        raise ValueError("Discount must be between 0 and 1")
    if discount == 1:
        return price
    if discount == 0:
        return price
    return price - (price * discount)


def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


import string

def word_frequencies(text):
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.translate(translator).lower()
    words = clean_text.split()
    frequencies = {}
    for word in words:
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies

def isPrime(n :  int):
    if n <= 1:
        return False    
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
