Project Summary
The project is a clinic management system developed in Python using Tkinter. It provides a user-friendly interface for managing professionals, patients, procedures, and appointments, ensuring efficient scheduling and patient care. The system features a secure login mechanism for professionals, utilizing a randomly generated access code for authentication.

Project Module Description
Main Application: Initializes the application and manages the main interface.
GUI: Contains various graphical components for user interaction, including login screens and main interface tabs.
Models: Defines data structures for professionals, patients, procedures, and appointments.
Database: Manages database connections and operations, including initialization and data manipulation.
Services: Contains business logic, including authentication services and code generation.
Utilities: Provides helper functions and common utilities for the application.
Directory Tree
/
├── main.py                          # Application entry point
├── models/                          # Data models
│   ├── __init__.py
│   ├── profissional.py               # Professional model (with access code)
│   ├── paciente.py                   # Patient model
│   ├── procedimento.py               # Procedure model
│   └── agendamento.py                # Appointment model
├── database/                        # Database management
│   ├── __init__.py
│   └── database_manager.py           # Handles database operations
├── services/                        # Business logic
│   ├── __init__.py
│   └── auth_service.py               # Authentication logic
├── gui/                             # GUI components
│   ├── __init__.py
│   ├── main_window.py                # Main application window
│   ├── login_window.py               # Login screen
│   ├── main_interface.py             # Main interface after login
│   ├── tabs/                        # Interface tabs
│   │   ├── __init__.py
│   │   ├── base_tab.py               # Base class for tabs
│   │   ├── calendario_tab.py          # Calendar tab
│   │   └── ...                       # Other tabs
│   └── dialogs/                     # Dialog windows
│       ├── __init__.py
│       └── profissional_dialog.py     # Dialog for professional registration
└── uploads/                         # Temporary uploads (if needed)
File Description Inventory
main.py: Initializes and runs the application.
models/: Contains classes for data representation.
database/: Manages database connections and queries.
services/: Implements business logic and authentication.
gui/: Provides the graphical user interface components.
Technology Stack
Python: Programming language used for development.
Tkinter: GUI toolkit for creating the user interface.
SQLite: Lightweight database for data storage.
Usage
Install dependencies (if any).
Run the application using:
python main.py
Follow the prompts to log in or register a new professional.