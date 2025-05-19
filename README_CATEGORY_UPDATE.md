# Category Integration Update Instructions

This update integrates categories with goals, values, and habits, allowing you to organize your life system items into meaningful categories.

## What's New

- **Categories as Containers**: Categories now act as true containers for goals, values, and habits
- **Category Selection**: You can assign categories when creating or editing any item
- **Category View**: The Categories screen now shows all related items in each category
- **Simplified Categories**: Removed parent-child relationship for categories for a simpler, flatter organization

## How to Update

Follow these steps to update your Life System application:

1. **Backup Your Data** (Automatic)
   - The update script will automatically create a backup of your database
   - Backups are stored in the `data` folder with timestamp in the filename

2. **Run the Update Script**
   - Open a command prompt/terminal in the LifeSystem directory
   - Run: `python update_db_schema.py`
   - The script will backup your database and recreate it with the new schema
   - **Note**: This process will reset your database, requiring you to re-enter your data

3. **Start the Application**
   - Run the application normally with your batch file or `python -m src.main`
   - Create new categories and assign them to your goals, values, and habits

## Troubleshooting

If you encounter any issues:

- The update script creates a backup of your database before making changes
- If needed, you can manually restore from a backup by renaming the backup file to `life_system.db`
- Look for backup files in the `data` folder with names like `life_system.db.backup_YYYYMMDD_HHMMSS`

## Feedback

We're continually improving the Life System application based on your feedback. If you have suggestions for further enhancements or encounter any issues, please let us know.

Enjoy your newly integrated Life System! 