# Life System

A personal life management system built with Python, PyQt5, and SQLAlchemy. Organize your goals, values, categories, and daily reflections in one place.

## Features

- **Goals Management**: Create, edit, and delete goals with various properties such as timeframe, priority, and target date.
- **Values Management**: Define and track your personal values with custom colors.
- **Categories Management**: Organize goals into categories with color coding.
- **Daily Reflections**: Record daily thoughts, achievements, and lessons learned with helpful prompts.
- **Color Coding**: Visual organization across all aspects of the system.

## Requirements

- Python 3.11+
- PyQt5
- SQLAlchemy
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone this repository.
2. Create a virtual environment:
   ```
   python -m venv venv311
   ```
3. Activate the virtual environment:
   - Windows: `.\venv311\Scripts\Activate.ps1`
   - Mac/Linux: `source venv311/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Ensure your virtual environment is activated.
2. Run the application:
   ```
   python src/main.py
   ```
3. For convenient access, you can use the included batch file:
   ```
   run_life_system.bat
   ```
4. To create a desktop shortcut:
   - Run the batch file (double-click or run from command prompt):
     ```
     create_shortcut.bat
     ```
   - After running the batch file, you'll find a "Life System" shortcut on your desktop.
   - Simply double-click the shortcut to launch the application.

## Project Structure

```
LifeSystem/
├── data/                # Database files
├── src/                 # Source code
│   ├── models/          # Database models
│   │   ├── goal.py      # Goal model definition
│   │   ├── value.py     # Value model definition
│   │   ├── category.py  # Category model definition
│   │   └── ...
│   ├── views/           # UI components
│   │   ├── goals.py     # Goals view
│   │   ├── values.py    # Values view
│   │   ├── categories.py # Categories view
│   │   └── ...
│   └── main.py          # Application entry point
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## Development Roadmap

### Phase 1 (Current)
- Basic goal management
- Value tracking
- Category organization
- Simple reflection system

### Phase 2 (Planned)
- Calendar integration
- Habit tracking
- Progress visualization
- Data export/import

### Phase 3 (Future)
- Mobile companion app
- Cloud synchronization
- Advanced analytics
- Integrated journaling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyQt5 for the GUI
- SQLAlchemy for database ORM
- Developed as a personal project for life organization 