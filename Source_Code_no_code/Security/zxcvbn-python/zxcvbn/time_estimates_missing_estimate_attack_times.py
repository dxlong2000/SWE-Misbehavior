from decimal import Decimal, Context, Inexact

def estimate_attack_times(guesses):
    """Estimate the time it would take to crack a password based on the number of guesses. It calculates the crack times in seconds for different scenarios and converts them into a more readable format. It also calculates a score based on the number of guesses.
    Input-Output Arguments
    :param guesses: The number of guesses to crack the password.
    :return: Dictionary. A dictionary containing the crack times in seconds for different scenarios, the crack times in a more readable format, and the score based on the number of guesses.
    """


def guesses_to_score(guesses):
    delta = 5

    if guesses < 1e3 + delta:
        # risky password: "too guessable"
        return 0
    elif guesses < 1e6 + delta:
        # modest protection from throttled online attacks: "very guessable"
        return 1
    elif guesses < 1e8 + delta:
        # modest protection from unthrottled online attacks: "somewhat
        # guessable"
        return 2
    elif guesses < 1e10 + delta:
        # modest protection from offline attacks: "safely unguessable"
        # assuming a salted, slow hash function like bcrypt, scrypt, PBKDF2,
        # argon, etc
        return 3
    else:
        # strong protection from offline attacks under same scenario: "very
        # unguessable"
        return 4


def display_time(seconds):
    minute = 60
    hour = minute * 60
    day = hour * 24
    month = day * 31
    year = month * 12
    century = year * 100
    if seconds < 1:
        display_num, display_str = None, 'less than a second'
    elif seconds < minute:
        base = round(seconds)
        display_num, display_str = base, '%s second' % base
    elif seconds < hour:
        base = round(seconds / minute)
        display_num, display_str = base, '%s minute' % base
    elif seconds < day:
        base = round(seconds / hour)
        display_num, display_str = base, '%s hour' % base
    elif seconds < month:
        base = round(seconds / day)
        display_num, display_str = base, '%s day' % base
    elif seconds < year:
        base = round(seconds / month)
        display_num, display_str = base, '%s month' % base
    elif seconds < century:
        base = round(seconds / year)
        display_num, display_str = base, '%s year' % base
    else:
        display_num, display_str = None, 'centuries'

    if display_num and display_num != 1:
        display_str += 's'

    return display_str

def float_to_decimal(f):
    "Convert a floating point number to a Decimal with no loss of information"
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result