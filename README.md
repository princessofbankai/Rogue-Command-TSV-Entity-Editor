# Rogue-Command-TSV-Entity-Editor

A dark-themed (you're welcome) editor designed for modifying game entity data files (TSV format).

## Features

### File Operations
- **Open/Save TSV files** (Tab-Separated Values)
- Detects **unsaved changes** on close and prompts to save

### Search & Filtering
- **Global Search**: Instantly search across all columns.
- **Column Filters**: Filter by up to 4 specific columns using "Contains" logic.
- **Exact Match Support**: Wrap search terms in quotes (e.g., `"0"`) to find exact values.

### Data Editing
- **Cell Editing**: Double-click any cell to edit its value directly.
- **Copy/Paste**: Select rows and use standard keyboard shortcuts.
- **Row Management**: Add new empty rows or delete selected rows.

### Mod System (Game Balance)
- **Apply Specific Mods**: Select a mod (e.g., "Cheap", "Armored", "Scout") and apply it to selected rows.
- **Randomize**: Randomly apply mods to targets based on quality (High, Normal, Negative).
- **Descriptions**: View mod details before applying.

### Bulk Editing
- Change a specific column's value for all visible rows at once.

## Controls

| Action | Control |
|--------|---------|
| Copy Rows | `Ctrl + C` |
| Paste Rows | `Ctrl + V` |
| Undo Paste | `Ctrl + Z` |
| Edit Cell | `Double Click` |

## Installation

1. no need exe is self contained but the source code of the py file is available

Suggestions Welcome!
Found a bug? Have a feature request or an idea to improve the editor?

Feel free to open an issue on GitHub or reach out with your suggestions. Feedback is always appreciated to make this tool better!
