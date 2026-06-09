# Smart Label Printer – ST-16
**Version 1.0**

A Windows desktop application for printing on ST-16 A4 label sheets (4×4 grid, 16 labels per sheet).
Designed to help you reuse partially-used sheets and prevent accidental double-printing.

### 📥 [Download Latest EXE (Windows)](https://github.com/vikasprajapat2/smart_lable_print/raw/main/dist/SmartLabelPrinter.exe)
*(Simply download and double-click to run! No installation required.)*

---

## Features
- True-to-life ST-16 A4 grid layout (2 columns × 8 rows)
- Modern Dark-Themed UI with CustomTkinter
- Click to select labels; double-click to edit content
- 4-line text per label with font size, bold, and alignment
- Three label states: **Empty** (white), **Filled** (yellow), **Printed** (green)
- Reprint protection with confirmation prompt
- Print preview showing exact A4 layout
- Direct Print & Download PDF options
- SQLite database – fully offline, no internet required
- Backup & restore database
- Search sheets by name, ID, or date

---

## Running from Source

### Prerequisites
- Python 3.8 or newer
- pip

### Install dependencies
```
python -m pip install -r requirements.txt
```

### Run
```
python app.py
```

---

## Building the EXE (Windows)

### Option 1 – Use the build script
Open your terminal in the project folder and run:
```powershell
.\build.bat
```

### Option 2 – Manual
```powershell
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller SmartLabelPrinter.spec --clean
```

The output file will be at:
```
dist\SmartLabelPrinter.exe
```

---

## Deploying to Another PC (No Installation Required!)

The `SmartLabelPrinter.exe` is a **fully standalone, portable application**. 

1. **Copy** `dist\SmartLabelPrinter.exe` to a USB drive, or send it via email/cloud storage.
2. **Transfer** it to any Windows 10/11 machine.
3. **Double-click** it to run!

**No Python, no installers, and no internet connection are required on the other PC.** 
*(Note: If Windows Defender shows a blue "Windows protected your PC" screen the first time you run it, simply click **More info** -> **Run anyway**).*

---

## Label Sheet Specification

| Property | Value |
|----------|-------|
| Sheet Type | ST-16 |
| Paper Size | A4 (210 × 297 mm) |
| Layout | 4 columns × 4 rows |
| Label Width | 99.1 mm |
| Label Height | 33.9 mm |
| Total Labels | 16 per sheet |

---

## How to Use

1. **Create a New Sheet** – Click `New Sheet` and enter a name.
2. **Edit Labels** – Double-click any label to enter text (up to 4 lines).
3. **Select for Printing** – Single-click labels to select (blue highlight).
4. **Preview** – Click `Preview` to see the exact print layout.
5. **Print** – Click `Print` to send selected labels to your printer.
6. After printing, labels turn **green** and are protected from accidental reprinting.
7. **Open an Existing Sheet** – Click `Open Sheet` to continue working on a saved sheet.

---

## Database

Data is stored in:
```
database/labels.db
```

Use **Backup Database** / **Restore Database** from the toolbar to protect your data.

---

## Folder Structure

```
SmartLabelPrinter/
├── app.py                  ← entry point
├── build.bat               ← Windows build script
├── SmartLabelPrinter.spec  ← PyInstaller spec
├── requirements.txt
├── database/
│   └── labels.db           ← SQLite database (auto-created)
├── ui/
│   ├── dashboard.py        ← main window
│   ├── label_editor.py     ← label edit popup
│   ├── preview.py          ← print preview
│   └── settings.py         ← settings dialog
├── services/
│   ├── database_service.py ← all DB operations
│   ├── print_service.py    ← PDF generation & printing
│   └── backup_service.py   ← backup / restore
└── backups/                ← auto-saved backups stored here
```
