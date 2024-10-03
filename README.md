# Beck View Projector

## Overview

Beck View Projector is a MicroPython project designed to simulate a Super 8 projector using a Raspberry Pi Pico. The system features real-time frame count and frames-per-second (FPS) display on an SPI OLED display, which provides clear visual feedback while the projector is running. The user can start and stop the projector using buttons wired to specific GPIO pins, simulating the operation of a real projector with LED indicators and on-screen feedback.

## Hardware Requirements

- **Raspberry Pi Pico**
- **SSD1306 OLED Display** (SPI version)
- **Two buttons** (for start and stop functionality)
- **LED indicator** (for operation status)
- **Wiring setup**:
    - OLED Display SPI Pins:
        - `MOSI`: GPIO 7
        - `SCK`: GPIO 6
        - `DC`: GPIO 8
        - `RES`: GPIO 9
        - `CS`: GPIO 5
    - Start button: GPIO 14
    - Stop button: GPIO 15
    - OK1 output: GPIO 12
    - EOF output: GPIO 13
    - LED indicator: GPIO 25

## Software Requirements

- **MicroPython**: Installed on the Raspberry Pi Pico
- **SSD1306 Driver**: Make sure to upload the `ssd1306.py` driver to the Pico before running the main code.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/beck-view-projector.git
   ```

2. **Upload the files to Raspberry Pi Pico** using tools like [Thonny](https://thonny.org/) or `ampy`.

   ```bash
   ampy --port /dev/ttyUSB0 put main.py
   ```

3. **Make sure the `ssd1306.py` driver is also uploaded** for handling the OLED display.

## Usage

Once the hardware is set up and code is uploaded:

1. **Power on your Raspberry Pi Pico**.
2. The OLED display will show the initial welcome message:

    ```
    beck-view
    projector
    Press button
    to start
    projector
    ```

3. **Press the start button** (connected to GPIO 14). This will start the simulated projector. The frame count and FPS will be displayed on the OLED screen:

    ```
    Frame <current_frame>
    FPS <calculated_fps>
    ```

4. **Press the stop button** (connected to GPIO 15) to stop the projector. The display will show the end-of-film (EOF) message:

    ```
    EOF reached
    Total frames <total_frames>
    ```

## Code Explanation

### `SPI_Display` Class

- Handles the OLED SPI display (SSD1306).
- Initializes the display and provides a method to show welcome messages and update the screen with frame information.
- Uses `display_welcome_message()` to present the initial startup screen.

### `Projector` Class

- Controls the projector simulation.
- Manages frame count, FPS calculations, and signal handling.
- Uses hardware interrupts on GPIO pins to start and stop the projector based on button presses.

### Main Loop

- Sets up hardware interrupts on GPIO pins for start and stop buttons.
- Runs a simple loop that blinks the LED while waiting for user input.

## Pin Assignments

| Component    | GPIO Pin |
|--------------|----------|
| Start Button | 14       |
| Stop Button  | 15       |
| OK1 Signal   | 12       |
| EOF Signal   | 13       |
| LED          | 25       |
| MOSI         | 7        |
| SCK          | 6        |
| DC           | 8        |
| RES          | 9        |
| CS           | 5        |

## Contributing

Feel free to submit issues or contribute by opening pull requests. We welcome any suggestions to improve the code or add new features.

## License

This project is licensed under the MIT License.
