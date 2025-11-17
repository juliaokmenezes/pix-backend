import random
import string


def gerar_iteration_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

