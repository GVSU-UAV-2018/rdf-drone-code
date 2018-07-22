

class MovingAverageEstimator:

    def __init__(self, rate, warmup):
        self.rate = rate
        self.warmup = warmup
        self.reset()

    def reset(self):
        self.estimate = None
        self.remaining_warmup = self.warmup

    def update(self, latest):
        if self.estimate is None:
            self.estimate = latest
        else:
            self.estimate = (
                self.estimate * self.rate
                + latest * (1 - self.rate))
        self.remaining_warmup = max(0, self.remaining_warmup - 1)
