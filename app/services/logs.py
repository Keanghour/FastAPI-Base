# app\services\logs.py

import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import shutil

# Configure logging
log_dir = "logs"  # Directory to store logs
os.makedirs(log_dir, exist_ok=True)  # Ensure the log directory exists
log_file = os.path.join(log_dir, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

# Function to mask sensitive data (only mask 'password')
def mask_sensitive_data(data: dict) -> dict:
    masked_data = data.copy()
    sensitive_keys = ["password"]  # Only mask 'password'
    
    for key in sensitive_keys:
        if key in masked_data:
            masked_data[key] = "***MASKED***"
    
    return masked_data

# Function to check log file age and rotate if needed
def rotate_logs():
    log_file_path = os.path.join(log_dir, "app.log")
    if os.path.exists(log_file_path):
        # Get the file's last modification time
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(log_file_path))
        now = datetime.now()
        diff = now - file_mod_time
        
        # If the log is older than 10 days, create a backup and clear it
        if diff >= timedelta(days=10):
            backup_log_file(log_file_path)

# Function to back up the log file with a date range
def backup_log_file(log_file_path):
    # Create a backup file name
    today = datetime.now()
    start_date = today - timedelta(days=10)
    backup_file_name = f"{start_date.strftime('%Y%m%d')}-{today.strftime('%Y%m%d')}.log"
    backup_file_path = os.path.join(log_dir, backup_file_name)

    # Back up the log file
    shutil.copy(log_file_path, backup_file_path)
    logger.info(f"Log file backed up to: {backup_file_path}")

    # Clear the log file
    open(log_file_path, 'w').close()
    logger.info("Log file cleared.")

# Start the scheduler to run log rotation every day
def start_log_rotation():
    scheduler = BackgroundScheduler()
    scheduler.add_job(rotate_logs, 'interval', days=1)
    scheduler.start()

