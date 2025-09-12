def discounted_sum(values: list[int | float], delta: float, initial_period: int = 0):
    """Calculated the discounted sum of a list of numbers.

    Args:
        values: The list of numbers to be discounted
        delta: The discount factor
        initial_period: The initial period of the list
            default: 0
    """
    discounted_values = [
        values[i] * delta ** (i + initial_period) for i in range(len(values))
    ]
    return sum(discounted_values)
