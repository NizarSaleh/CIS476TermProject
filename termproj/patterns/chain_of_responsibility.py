# patterns/chain_of_responsibility.py
"""
Chain of Responsibility pattern for password recovery.
Each handler checks one security question in sequence.
If any answer is incorrect, the chain stops.
"""
class Handler:
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, request):
        if self.next_handler:
            return self.next_handler.handle(request)
        return True

class SecurityQuestionHandler1(Handler):
    def handle(self, request):
        if request["answer1"].strip().lower() != request["correct_answer1"].strip().lower():
            print("[CoR] Incorrect answer for question 1.")
            return False
        print("[CoR] Correct answer for question 1.")
        return super().handle(request)

class SecurityQuestionHandler2(Handler):
    def handle(self, request):
        if request["answer2"].strip().lower() != request["correct_answer2"].strip().lower():
            print("[CoR] Incorrect answer for question 2.")
            return False
        print("[CoR] Correct answer for question 2.")
        return super().handle(request)

class SecurityQuestionHandler3(Handler):
    def handle(self, request):
        if request["answer3"].strip().lower() != request["correct_answer3"].strip().lower():
            print("[CoR] Incorrect answer for question 3.")
            return False
        print("[CoR] Correct answer for question 3.")
        return super().handle(request)
