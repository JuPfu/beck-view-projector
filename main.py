import time

import micropython
from machine import Pin, Timer


class Projector:
    OFF = 0
    ON = 1

    # Define the GPIO pins for the projector's components
    led_pin = Pin(25, Pin.OUT, value=OFF)  # LED indicator for operation

    start_pin = Pin(14, Pin.IN, value=OFF)  # Input for starting the projector
    stop_pin = Pin(15, Pin.IN, value=OFF)  # Input for stopping the projector

    ok1_pin = Pin(12, Pin.OUT, value=ON)  # Pin to send the OK1 signal (indicating frame advancement)
    eof_pin = Pin(13, Pin.OUT, value=ON)  # Pin to send EOF (end-of-film) signal

    count = -1  # Frame counter, -1 means not running

    timer = Timer()  # Timer for periodic signal sending

    timer_started = False  # Flag to track if the projector is running
    start_time = 0  # Used to calculate time between signals

    def start_pin_isr(self, pin) -> None:
        """Interrupt service routine triggered by the start_pin."""
        micropython.schedule(self.setup_ok1_signal, None)

    def setup_ok1_signal(self, _) -> None:
        """Initializes the OK1 signal transmission and starts the timer."""
        if not self.timer_started:  # Prevents reinitialization while running
            self.count = 0
            self.timer_started = True
            self.start_time = time.ticks_ms()  # Record start time in milliseconds

            # Start the timer to call 'send_ok1_signal' at 5 Hz (5 frames per second)
            self.timer.init(mode=Timer.PERIODIC, freq=5, callback=self.send_ok1_signal)

    def send_ok1_signal(self, timer) -> None:
        """Send OK1 signal (frame advancement) every timer tick."""
        current_time = time.ticks_ms()
        print(f"Time diff: {time.ticks_diff(current_time, self.start_time)} ms, Frame count: {self.count}")
        self.start_time = current_time  # Update start_time for next frame

        # Flash the LED and toggle the OK1 pin to simulate a frame advancing signal
        self.led_pin.value(self.ON)  # Turn LED ON
        self.ok1_pin.value(self.OFF)  # Send OK1 signal
        time.sleep_us(8000)  # Wait for 8 milliseconds (8000 microseconds)
        self.ok1_pin.value(self.ON)  # Reset OK1 signal
        self.led_pin.value(self.OFF)  # Turn LED OFF

        self.count += 1  # Increment the frame counter

    def stop_pin_isr(self, pin) -> None:
        """Interrupt service routine triggered by the stop_pin."""
        micropython.schedule(self.setup_eof_signal, None)

    def setup_eof_signal(self, _) -> None:
        """Stops the timer and sends EOF signal."""
        if self.timer_started:
            self.timer_started = False
            self.timer.deinit()  # Stop the timer
            self.send_eof_signal()

    def send_eof_signal(self) -> None:
        """Send End-Of-Film signal to indicate projector has stopped."""
        self.led_pin.value(self.ON)  # Turn LED ON
        self.eof_pin.value(self.OFF)  # Send EOF signal
        time.sleep_us(8000)  # Wait for 8 milliseconds (8000 microseconds)
        self.eof_pin.value(self.ON)  # Reset EOF signal
        self.led_pin.value(self.OFF)  # Turn LED OFF
        print(f"EOF reached. Total frames: {self.count}")
        self.count = -1  # Reset frame counter


if __name__ == '__main__':
    # Initialize the projector
    projector = Projector()
    projector.led_pin.value(projector.ON)
    print('<<<beck-view-projector initialized>>>')

    # Set up interrupts for the start and stop buttons (falling edge detection)
    projector.start_pin.irq(handler=projector.start_pin_isr, trigger=Pin.IRQ_FALLING)
    projector.stop_pin.irq(handler=projector.stop_pin_isr, trigger=Pin.IRQ_FALLING)

    # Simple LED blinking loop to indicate the system is ready
    for _ in range(10):
        projector.led_pin.value(projector.OFF)
        time.sleep_ms(100)  # LED OFF for 100 ms
        projector.led_pin.value(projector.ON)
        time.sleep_ms(100)  # LED ON for 100 ms
