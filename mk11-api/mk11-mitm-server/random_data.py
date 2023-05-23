import random
import string

def get_random_value(current_depth = 0):
    if current_depth > 5:
        return
    if bool(random.getrandbits(1)):
        return get_random_dict(current_depth + 1)
    elif bool(random.getrandbits(1)):
        return get_random_string()
    elif bool(random.getrandbits(1)):
        return get_random_int()
    elif bool(random.getrandbits(1)):
        return get_random_list(current_depth + 1)

def get_random_dict(current_depth = 0):
    return generate_random_dict(random.randint(1, 10), current_depth + 1)

def get_random_string():
    return "".join(random.choices(string.ascii_letters, k=random.randint(1, 10)))

def get_random_int():
    return random.randint(0, 100)

def get_random_list(current_depth = 0):
    if current_depth > 4:
        return get_random_int()
    return generate_random_list(random.randint(1, 10))

def generate_random_list(size, current_depth = 0):
    return [get_random_value(current_depth + 1) for _ in range(size)]

def generate_random_dict(size = None, current_depth = 0):
    if current_depth > 4:
        return get_random_int()

    if size is None:
        size = random.randint(1, 5)
    return {
        get_random_string(): get_random_value(current_depth + 1)
        for _ in range(size)
    }

def get_random_collection():
    if bool(random.getrandbits(1)):
        return get_random_dict()
    else:
        return get_random_list()
