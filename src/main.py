import time

import micropython
from machine import Pin, Timer, SPI, ADC

from ssd1306 import SSD1306_SPI


class SPI_Display:
    OFF = 0
    ON = 1

    def __init__(self) -> None:
        """Initialize the SPI display with the correct GPIO pins for the OLED."""
        # OLED display GPIO pin mapping:
        # mosi: pin 7, sck: pin 6, dc: pin 8, res: pin 9, cs: pin 5
        spi = SPI(0, 100000, mosi=Pin(7), sck=Pin(6))
        self.ssd1306_spi = SSD1306_SPI(128, 64, spi, Pin(8), Pin(9), Pin(5))
        self.ssd1306_spi.init_display()
        self.display_welcome_message()

    def display_welcome_message(self) -> None:
        """Display a welcome message when the projector is powered on."""
        self.ssd1306_spi.fill(0)  # Clear the display
        self.ssd1306_spi.fill_rect(0, 0, 128, 16, 2)  # Draw a filled rectangle for the title
        self.ssd1306_spi.text("beck-view", 0, 0, 0)
        self.ssd1306_spi.text("projector", 0, 8, 0)
        self.ssd1306_spi.text("Press button", 0, 25)
        self.ssd1306_spi.text("to start", 0, 35)
        self.ssd1306_spi.text("projector", 0, 45)
        self.ssd1306_spi.show()  # Refresh the display to show changes

    def clear_display(self) -> None:
        """Helper function to clear the display for new updates."""
        self.ssd1306_spi.fill(0)  # Clear the display
        self.ssd1306_spi.show()  # Apply the clear action


class Projector:
    OFF = 0
    ON = 1

    def __init__(self, display: SPI_Display) -> None:
        """Initialize the projector and bind it to the display."""
        self.display = display

    adc0 = ADC(0)
    adc_timer = Timer()

    # GPIO pin setup for projector components
    led_pin = Pin(25, Pin.OUT, pull=Pin.PULL_DOWN, value=OFF)  # LED for visual status
    start_pin = Pin(14, Pin.IN, value=OFF)  # Input for start button
    stop_pin = Pin(15, Pin.IN, value=OFF)  # Input for stop button

    ok1_pin = Pin(12, Pin.OUT, pull=Pin.PULL_DOWN, value=ON)  # Pin to send OK1 (frame signal)
    eof_pin = Pin(13, Pin.OUT, pull=Pin.PULL_DOWN, value=ON)  # Pin to send EOF (end of film)

    count = -1  # Frame counter, -1 means the projector is idle
    timer = Timer()  # Timer for periodic frame signal
    timer_started = False  # Flag to track projector state
    start_time = 0  # Time reference for frame timing

    freq = 5

    def start_pin_isr(self, pin) -> None:
        """Interrupt triggered by the start button press."""
        micropython.schedule(self.setup_ok1_signal, None)

    def setup_ok1_signal(self, _) -> None:

        """Start sending OK1 signals if the projector is not already running."""
        if not self.timer_started:
            self.adc_timer.deinit()  # remove timer for potentiometer
            self.adc_timer = None

            self.count = 0
            self.timer_started = True
            self.start_time = time.ticks_ms()  # Set time reference

            # Start timer at 5 Hz (5 frames per second)
            self.timer.init(mode=Timer.PERIODIC, freq=self.freq, callback=self.send_ok1_signal)

    def send_ok1_signal(self, timer) -> None:
        """Send OK1 signal to indicate frame progression."""
        current_time = time.ticks_ms()
        time_diff = time.ticks_diff(current_time, self.start_time)
        self.start_time = current_time  # Update time reference

        # Flash the LED and toggle OK1 pin to simulate frame signal
        self.led_pin.value(self.ON)  # Turn LED ON
        self.ok1_pin.value(self.OFF)  # Activate OK1
        time.sleep_us(8000)  # Wait for 8 milliseconds (8000 microseconds)
        self.ok1_pin.value(self.ON)  # Deactivate OK1
        self.led_pin.value(self.OFF)  # Turn LED OFF

        # Update the display with the current frame count and FPS
        self.display.clear_display()  # Clear display before writing new info
        self.display.ssd1306_spi.text(f"Frame {self.count}", 0, 25)
        fps = 1000.0 / time_diff  # Calculate FPS from time difference
        self.display.ssd1306_spi.text(f"FPS   {fps:.2f}", 0, 35)
        self.display.ssd1306_spi.show()  # Refresh display with new data

        self.count += 1  # Increment frame counter

    def stop_pin_isr(self, pin) -> None:
        """Interrupt triggered by the stop button press."""
        micropython.schedule(self.setup_eof_signal, None)

    def setup_eof_signal(self, _) -> None:
        """Stop the projector and send an EOF signal."""
        if self.timer_started:
            self.timer_started = False
            self.timer.deinit()  # Stop the timer
            self.send_eof_signal()

    def send_eof_signal(self) -> None:
        """Send an EOF signal to indicate the projector has stopped."""
        self.led_pin.value(self.ON)  # Turn LED ON
        self.eof_pin.value(self.OFF)  # Send EOF signal
        time.sleep_us(8000)  # Wait for 8 milliseconds (8000 microseconds)
        self.eof_pin.value(self.ON)  # Reset EOF signal
        self.led_pin.value(self.OFF)  # Turn LED OFF

        # Display the end of film message with total frames projected
        self.display.clear_display()
        self.display.ssd1306_spi.text(f"EOF reached", 0, 25)
        self.display.ssd1306_spi.text(f"Frames {self.count}", 0, 35)
        self.display.ssd1306_spi.show()
        self.count = -1  # Reset frame counter

        if self.adc_timer != None:
            self.adc_timer.deinit()
        self.setup_adc_signal()

    def setup_adc_signal(self) -> None:
        """Interrupt triggered by the stop button press."""
        self.adc_timer.init(mode=Timer.PERIODIC, freq=5, callback=self.read_adc_signal)

    def read_adc_signal(self, timer) -> None:
        self.freq = round(self.adc0.read_u16() / 65535 * 24)
        self.display.ssd1306_spi.fill_rect(0, 55, 128, 8, 0)  # Draw a filled rectangle for the title
        self.display.ssd1306_spi.text(f"FPS   {self.freq:2d}", 0, 55)
        self.display.ssd1306_spi.show()  # Refresh display with new data


if __name__ == '__main__':
    # Initialize the OLED display and projector
    spi_display = SPI_Display()
    projector = Projector(spi_display)

    projector.led_pin.value(projector.ON)

    # Set up interrupts for start/stop buttons on falling edge (button pressed)
    projector.start_pin.irq(handler=projector.start_pin_isr, trigger=Pin.IRQ_FALLING)
    projector.stop_pin.irq(handler=projector.stop_pin_isr, trigger=Pin.IRQ_FALLING)
    projector.setup_adc_signal()

    # Simple LED blink loop to indicate system readiness
    for _ in range(10):
        projector.led_pin.value(projector.OFF)
        time.sleep_ms(100)  # LED OFF for 100ms
        projector.led_pin.value(projector.ON)
        time.sleep_ms(100)  # LED ON for 100ms
