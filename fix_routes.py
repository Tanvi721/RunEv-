import os
import glob

# Ensure we're in the right directory
os.chdir(r"c:\Users\Pramod\OneDrive\Desktop\RUNEV")

rename_map = {
    "pages/login.py": "pages/01_Login.py",
    "pages/register.py": "pages/02_Register.py",
    "pages/search.py": "pages/03_Search.py",
    "pages/dashboard.py": "pages/04_Dashboard.py",
    "pages/booking.py": "pages/05_Booking.py",
    "pages/payment.py": "pages/06_Payment.py",
    "pages/admin.py": "pages/07_Admin_Panel.py"
}

# 1. Update text inside files
all_files = glob.glob("pages/*.py") + ["app.py"]
for filepath in all_files:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace occurrences
        content = content.replace('"pages/login.py"', '"pages/01_Login.py"')
        content = content.replace('"pages/register.py"', '"pages/02_Register.py"')
        content = content.replace('"pages/search.py"', '"pages/03_Search.py"')
        content = content.replace('"pages/dashboard.py"', '"pages/04_Dashboard.py"')
        content = content.replace('"pages/booking.py"', '"pages/05_Booking.py"')
        content = content.replace('"pages/payment.py"', '"pages/06_Payment.py"')
        content = content.replace('"pages/admin.py"', '"pages/07_Admin_Panel.py"')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

# 2. Rename the files
for old_path, new_path in rename_map.items():
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

print("Renaming and updating complete!")
