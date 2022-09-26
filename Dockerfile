FROM python:3.9-buster

# Chaning default workspace
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install -r /app/requirements.txt

# Copy everything
COPY . .

# Run the damn project
CMD ["python", "bot.py"]