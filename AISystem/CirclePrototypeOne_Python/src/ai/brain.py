from .evaluator import Evaluator

class Brain:
    def __init__(self):
        self.evaluators: list[Evaluator] = []