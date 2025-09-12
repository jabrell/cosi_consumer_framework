from cosi_consumer_framework.utils import discounted_sum


def test_discounted_sum():
    assert discounted_sum([1] * 5, 0.9) == 4.0951
    assert round(discounted_sum([1] * 5, 0.9, 5), 6) == 2.418116
