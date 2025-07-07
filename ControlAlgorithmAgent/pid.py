# pid.py
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, sample_time):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.sample_time = sample_time
        self.clear()

    def clear(self):
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.int_error = 0.0
        self.last_time = None

    def update(self, feedback_value, current_time):
        error = self.setpoint - feedback_value
        delta_time = self.sample_time if self.last_time is None else current_time - self.last_time

        self.PTerm = self.Kp * error
        self.ITerm += error * delta_time

        if delta_time > 0:
            self.DTerm = (error - self.last_error) / delta_time

        self.last_error = error
        self.last_time = current_time

        return self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
