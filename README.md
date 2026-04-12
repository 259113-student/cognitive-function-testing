# cognitive-function-testing

# Cognitive Function Assessment Suite

This project is a desktop application developed with Python and PyQt6, designed to administer a series of cognitive tests. It provides a user-friendly interface for users to assess various aspects of their cognitive functions, such as attention, processing speed, and short-term memory.

## Features

- **User-Friendly Interface:** A clean and intuitive GUI for easy navigation.
- **Multiple Cognitive Tests:** Includes a selection of standardized tests:
  - **Stroop Test:** Measures selective attention and processing speed.
  - **Delayed Matching-to-Sample (DMS):** Assesses short-term visual memory.
- **Pre-Test Instructions:** Clear, stylized instructions are provided before each test begins.
- **Modular Architecture:** The application is structured to easily allow for the addition of new tests in the future.

## Tech Stack

- **Language:** Python 3
- **GUI Framework:** PyQt6
- **Libraries:** See `requirements.txt` for a full list of dependencies.

## Project Structure

The project is organized into a modular structure to separate different components of the application:

```
.
├── app/
│   ├── assets/             # Icons and other image assets
│   │   ├── brain-icon.png
│   │   └── pending-icon.png
│   ├── tests/              # Test screens
│   │   ├── base_test_screen.py   # In progres sample screen - to remove in later steps
│   │   ├── dms_test_screen.py    # Individual test screen for DMS Test - ready for logic implementation
│   │   └── stroop_test_screen.py # Individual test screen for Stroop Test - ready for logic implementation
│   ├── test_instructions_screen.py # Screen for displaying test instructions
│   ├── test_selection_screen.py    # Screen for selecting a test
│   └── welcome_screen.py           # Initial welcome screen
├── main.py                 # Main application entry point
└── requirements.txt        # Project dependencies
```

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Once the setup is complete, you can run the application with the following command:

```bash
python main.py
```

This will launch the main window of the Cognitive Function Assessment Suite.
