import bisect
import itertools

from random import Random
from typing import Generator, Iterable, Optional, Sequence, TypeVar

from faker.generator import random as mod_random


def random_sample(random: Optional[Random] = None) -> float:
    if random is None:
        random = mod_random
    return random.uniform(0.0, 1.0)


def cumsum(it: Iterable[float]) -> Generator[float, None, None]:
    total: float = 0
    for x in it:
        total += x
        yield total


T = TypeVar("T")


def choices_distribution_unique(
    a: Sequence[T],
    p: Optional[Sequence[float]],
    random: Optional[Random] = None,
    length: int = 1,
) -> Sequence[T]:
    # As of Python 3.7, there isn't a way to sample unique elements that takes
    # weight into account.
    """This function generates a sequence of unique choices based on the given input sequence and their corresponding probabilities. It ensures that the generated choices are unique and takes into account the weight of each choice.
    Input-Output Arguments
    :param a: Sequence[T]. The input sequence of elements to choose from.
    :param p: Optional[Sequence[float]]. The probabilities associated with each element in the input sequence.
    :param random: Optional[Random]. The random number generator to be used. If not provided, the default random generator is used.
    :param length: int. The number of unique choices to generate. Defaults to 1.
    :return: Sequence[T]. A sequence of unique choices based on the input sequence and their probabilities.
    """


def choices_distribution(
    a: Sequence[T],
    p: Optional[Sequence[float]],
    random: Optional[Random] = None,
    length: int = 1,
) -> Sequence[T]:
    if random is None:
        random = mod_random

    if p is not None:
        assert len(a) == len(p)

    if hasattr(random, "choices"):
        if length == 1 and p is None:
            return [random.choice(a)]
        else:
            return random.choices(a, weights=p, k=length)
    else:
        choices = []

        if p is None:
            p = itertools.repeat(1, len(a))  # type: ignore

        cdf = list(cumsum(p))  # type: ignore
        normal = cdf[-1]
        cdf2 = [i / normal for i in cdf]
        for i in range(length):
            uniform_sample = random_sample(random=random)
            idx = bisect.bisect_right(cdf2, uniform_sample)
            item = a[idx]
            choices.append(item)
        return choices