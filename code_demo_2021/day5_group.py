"""
--- Day 5: Doesn't He Have Intern-Elves For This? ---

Santa needs help figuring out which strings in his text file are naughty or nice.
How many strings are nice?
"""
def is_nice(string):
    """Checks whether as string is nice or naughty.

    Strings are nice if:

    1. It does not contain the strings ab, cd, pq, or xy, even if they are part of
       one of the other requirements.

    2. It contains at least three vowels (aeiou only), like aei, xazegov, or
       aeiouaeiouaeiou.

    3. It contains at least one letter that appears twice in a row, like xx,
       abcdde (dd), or aabbccdd (aa, bb, cc, or dd).

    Parameters
    ----------
    string : str
        string to check

    Returns
    -------
    is_nice : bool
        Whether the string was nice or naughty.
    """
    # First condition
    if (
        ('ab' in string) or
        ('cd' in string) or
        ('pq' in string) or
        ('xy' in string)
    ):
        return False  # Naughty string!

    # Second condition
    vowels = ['a', 'e', 'i', 'o', 'u']
    num_vowels_in_string = 0
    for vowel in vowels:
        num_vowels_in_string += string.count(vowel)
    if num_vowels_in_string < 3:
        return False  # Naughty string!

    # Third condition
    num_duplicates = 0
    for i in range(len(string) - 1):  # -1 because of out of bounds errors
        if string[i] == string[i + 1]:
            num_duplicates += 1
    if num_duplicates == 0:
        return False  # Naughty string!

    return True


def test_is_nice():
    # ugknbfddgicrmopn is nice because it has at least three vowels
    # (u...i...o...), a double letter (...dd...), and none of the disallowed
    # substrings.
    assert is_nice('ugknbfddgicrmopn')

    # aaa is nice because it has at least three vowels and a double letter, even
    # though the letters used by different rules overlap.
    assert is_nice('aaa')

    # jchzalrnumimnmhp is naughty because it has no double letter.
    assert not is_nice('jchzalrnumimnmhp')

    # haegwjzuvuyypxyu is naughty because it contains the string xy.
    assert not is_nice('haegwjzuvuyypxyu')

    # dvszwmarrgswjxmb is naughty because it contains only one vowel.
    assert not is_nice('dvszwmarrgswjxmb')


if __name__ == '__main__':
    num_nice_strings = 0
    with open('day5_input.txt') as f:
        for string in f:
            if is_nice(string):
                num_nice_strings += 1

    print('The solution to part1 is:', num_nice_strings)
