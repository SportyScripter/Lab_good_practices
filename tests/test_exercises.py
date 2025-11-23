from exercises_to_test.exercises import (
    is_palindrome,
    fibonacci,
    count_vowels,
    calculate_discount,
    flatten_list,
    word_frequencies,
    isPrime,
)


def test_is_palindrome():
    answer_to_test_is_palindorme = {
        "kajak": True,
        "kobyla ma maly bok": True,
        "python": False,
        "": True,
        "A": True,
    }
    for text, expected in answer_to_test_is_palindorme.items():
        assert is_palindrome(text) == expected


def test_fibonacci():
    answer_to_test_fibonacci = {
        0: 0,
        1: 1,
        2: 1,
        5: 5,
        10: 55,
    }
    for n, expected in answer_to_test_fibonacci.items():
        assert fibonacci(n) == expected


def test_count_vowels():
    answer_to_test_count_vowels = {
        "Python": 2,
        "AEIOUY": 6,
        "bcd": 0,
        "": 0,
    }
    for text, expected in answer_to_test_count_vowels.items():
        assert count_vowels(text) == expected


def test_calculate_discount():
    answer_to_test_calculate_discount = {
        (100, 0.2): 80,
        (50, 0): 50,
        (200, 1): 200,
    }
    for (price, discount), expected in answer_to_test_calculate_discount.items():
        assert calculate_discount(price, discount) == expected

    try:
        calculate_discount(100, -0.1)
    except ValueError as e:
        assert str(e) == "Discount must be between 0 and 1"

    try:
        calculate_discount(100, 1.5)
    except ValueError as e:
        assert str(e) == "Discount must be between 0 and 1"


def test_flatten_list():
    test_cases = [
        ([1, 2, 3], [1, 2, 3]),
        ([1, [2, 3], [4, [5]]], [1, 2, 3, 4, 5]),
        ([], []),
        ([[[1]]], [1]),
        ([1, [2, [3, [4]]]], [1, 2, 3, 4]),
    ]

    for nested_list, expected in test_cases:
        result = flatten_list(nested_list)

        assert (
            result == expected
        ), f"Błąd dla wejścia: {nested_list}. Oczekiwano {expected}, otrzymano {result}"


def test_word_frequencies():
    test_cases = [
        ("To be or not to be", {"to": 2, "be": 2, "or": 1, "not": 1}),
        ("Hello, hello!", {"hello": 2}),
        ("", {}),
        ("Python Python python", {"python": 3}),
        (
            "Ala ma kota, a kot ma Ale.",
            {"ala": 1, "ma": 2, "kota": 1, "a": 1, "kot": 1, "ale": 1},
        ),
    ]

    for text, expected in test_cases:
        result = word_frequencies(text)
        assert (
            result == expected
        ), f"Błąd dla wejścia: '{text}'.\nOczekiwano: {expected}\nOtrzymano: {result}"

    print("Wszystkie testy przeszły pomyślnie!")


def test_isPirme():
    answer_to_test_isPrime = {
        2: True,
        3: True,
        4: False,
        0: False,
        1: False,
        5: True,
        97: True,
    }
    for n, expected in answer_to_test_isPrime.items():
        assert isPrime(n) == expected
