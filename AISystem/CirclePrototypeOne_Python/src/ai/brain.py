from .evaluator import IEvaluator

class Brain:
    def __init__(self):
        self.evaluators: list[IEvaluator] = []