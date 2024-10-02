# Beck View Projector

This project simulates the functionality of a vintage Super 8 projector using a **Raspberry Pi Zero (RP2)**, leveraging MicroPython. The `beck-view-projector` project is part of the larger `beck-view-digitize` initiative, which focuses on digitizing Super 8 films.

## Features

- **Start & Stop simulation**: Controls to start and stop the projector using buttons.
- **Frame advance emulation**: The OK1 signal is used to simulate the frame-by-frame advancement in a real Super 8 projector.
- **End of film (EOF) signal**: The projector emits an EOF signal when the simulation ends.
- **Visual feedback**: An LED on the Raspberry Pi is used to indicate different states of the projector.
  
## Hardware Requirements

- **Raspberry Pi Zero (RP2)**.
- **LED** connected to Pin 25 for visual feedback.
- **Two buttons** connected to GPIO pins for starting and stopping the projector.
  - **Start button** (connected to GPIO Pin 14) - Starts the projector.
  - **Stop button** (connected to GPIO Pin 15) - Stops the projector.
- **Two output pins** for signaling:
  - **OK1** (connected to GPIO Pin 12) - Simulates the frame advance.
  - **EOF** (connected to GPIO Pin 13) - Simulates the end-of-film signal.

## Getting Started

### Prerequisites

Ensure that you have:

- A Raspberry Pi Zero (RP2) with MicroPython installed.
- The necessary hardware setup (buttons, LED).
- USB or SSH access to the Raspberry Pi for uploading the code.

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/beck-view-projector.git
   ```

2. **Upload the code to the Raspberry Pi Zero**:

   Use a tool like `rshell` or `mpremote` to upload the `projector.py` script to your Raspberry Pi Zero.

   Example with `rshell`:

   ```bash
   rshell cp projector.py /pyboard/
   ```

3. **Connect hardware components** according to the pin configuration mentioned in the **Hardware Requirements** section.

### Running the Projector Simulation

1. **Power up** the Raspberry Pi Zero.
2. The simulation begins when the **Start button** (connected to GPIO 14) is pressed.
3. The projector simulates frame advancement with the **OK1 signal**.
4. Press the **Stop button** (connected to GPIO 15) to stop the projector and emit the **EOF signal**.

### Example Output

```
<<<beck-view-projector
time.ticks_diff(self.stop, self.start)=204   self.count=1
time.ticks_diff(self.stop, self.start)=200   self.count=2
EOF self.count=10
```

- **OK1 signal**: Simulates the frame advancement in Super 8 projection.
- **EOF signal**: Indicates the end of the simulated film sequence.

## Code Overview

The code uses MicroPython's hardware libraries (`machine` and `Timer`) to interact with the Raspberry Pi's GPIO pins. It defines a `Projector` class that manages the core logic of starting and stopping the simulation.

### Key Methods

- **`start_pin_isr(self, pin)`**: Interrupt service routine triggered when the start button is pressed.
- **`setup_ok1_signal(self, pin)`**: Prepares the OK1 signal to simulate frame advancement.
- **`send_ok1_signal(self, timer)`**: Sends the OK1 signal periodically.
- **`stop_pin_isr(self, pin)`**: Interrupt service routine triggered when the stop button is pressed.
- **`setup_eof_signal(self, pin)`**: Handles the EOF signal when the simulation stops.
- **`send_eof_signal(self)`**: Sends the EOF signal to indicate the end of the simulation.

### Timer and Signals

- **Timer**: A hardware timer is used to send periodic OK1 signals at 5 Hz, simulating the projector's frame rate.
- **OK1 and EOF signals**: Output signals that simulate the projector's physical behavior.

## Future Enhancements

- **Speed control**: Implement a feature to change the frame rate dynamically.
- **Pause/resume functionality**: Allow pausing and resuming the projector simulation.
- **Enhanced feedback**: Use additional LEDs or an LCD to display more detailed feedback.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Feel free to modify the README as needed, especially with the repository link and any project-specific details!