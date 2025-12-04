# #4: File for managing const values, tokens, and keys
import os

# Telegram Config
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# TwelveData Config
TD_API_KEY = "YOUR_TWELVEDATA_API_KEY"
SYMBOL = "XAU/USD"

# Data Fetching Settings
# #1: Calculate the necessary number of candles
# History size 100 ensures enough data for Ichimoku (52 candles) and S/R (100 candles).
HISTORY_SIZE = 100 
INTERVALS = ["15min", "30min", "1h"]

# File paths
TRIGGER_FILE = "trigger.txt"