# Use the official Python 3.10 image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /bot

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire bot source code to the container
COPY . .

# Health check to ensure the bot is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s \
    CMD pgrep -f bot.py || exit 1

# Command to run the bot
CMD ["python", "bot.py"]