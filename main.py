import time

import micropython
from machine import Pin, Timer, SPI

from ssd1306 import SSD1306_SPI


class SPI_Display:
    OFF = 0
    ON = 1

    def __init__(self) -> None:
        # GPIO pins for attached oled spi display
        # mosi: pin 7
        # sck:  pin 6
        # dc:   pin 8
        # res:  pin 9
        # cs:   pin 5

        spi = SPI(0, 100000, mosi=Pin(7), sck=Pin(6))
        self.ssd1306_spi = SSD1306_SPI(128, 64, spi, Pin(8), Pin(9), Pin(5))
        self.ssd1306_spi.init_display()
        self.hello()

    def hello(self) -> None:
        self.ssd1306_spi.fill(0)
        self.ssd1306_spi.show()
        self.ssd1306_spi.fill_rect(0, 0,  128,  16, 2)
        self.ssd1306_spi.text("beck-view", 0, 0, 0)
        self.ssd1306_spi.text("projector", 0, 8, 0)
        self.ssd1306_spi.text("Press button", 0, 25)
        self.ssd1306_spi.text("to start", 0, 35)
        self.ssd1306_spi.text("projector", 0, 45)
        self.ssd1306_spi.show()


class Projector:
    OFF = 0
    ON = 1

    def __init__(self, display: SPI_Display) -> None:
        self.display = display

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
        time_diff = time.ticks_diff(current_time, self.start_time)
        self.start_time = current_time  # Update start_time for next frame

        # Flash the LED and toggle the OK1 pin to simulate a frame advancing signal
        self.led_pin.value(self.ON)  # Turn LED ON
        self.ok1_pin.value(self.OFF)  # Send OK1 signal
        time.sleep_us(8000)  # Wait for 8 milliseconds (8000 microseconds)
        self.ok1_pin.value(self.ON)  # Reset OK1 signal
        self.led_pin.value(self.OFF)  # Turn LED OFF

        self.display.ssd1306_spi.fill(0)
        self.display.ssd1306_spi.show()
        self.display.ssd1306_spi.text(f"Frame {self.count}", 0, 0)
        fps: float = 1000.0 / time_diff
        self.display.ssd1306_spi.text(f"FPS   {fps:.2f}", 0, 10)
        self.display.ssd1306_spi.show()

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
        self.display.ssd1306_spi.fill(0)
        self.display.ssd1306_spi.show()
        self.display.ssd1306_spi.text(f"EOF reached", 0, 0)
        self.display.ssd1306_spi.text(f"Total frames {self.count}", 0, 10)
        self.display.ssd1306_spi.show()
        self.count = -1  # Reset frame counter


if __name__ == '__main__':
    # Initialize the projector
    spi_display = SPI_Display()
    projector = Projector(spi_display)
    projector.led_pin.value(projector.ON)

    # Set up interrupts for the start and stop buttons (falling edge detection)
    projector.start_pin.irq(handler=projector.start_pin_isr, trigger=Pin.IRQ_FALLING)
    projector.stop_pin.irq(handler=projector.stop_pin_isr, trigger=Pin.IRQ_FALLING)

    # Simple LED blinking loop to indicate the system is ready
    for _ in range(10):
        projector.led_pin.value(projector.OFF)
        time.sleep_ms(100)  # LED OFF for 100 ms
        projector.led_pin.value(projector.ON)
        time.sleep_ms(100)  # LED ON for 100 ms
