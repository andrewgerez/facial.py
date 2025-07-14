VENV_DIR := .venv
PYTHON := $(VENV_DIR)/Scripts/python.exe
PIP := $(VENV_DIR)/Scripts/pip.exe
SCRIPT := app/facial_recognition.py
DB := faces.db

REQUIREMENTS := face_recognition opencv-python

.PHONY: all venv install run clean reset-db help

all: help

help:
	@echo "Comandos disponíveis:"
	@echo "  make venv         - Create the virtual environment"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the application"
	@echo "  make clean        - Clean temporary files"
	@echo "  make reset-db     - Reset the database"
	@echo "  make all          - Show this help message"

venv:
	@echo "🔧 Creating the virtual environment in $(VENV_DIR)..."
	@python -m venv $(VENV_DIR)

install: venv
	@echo "📦 Installing dependencies..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install $(REQUIREMENTS)
	@$(PIP) install git+https://github.com/ageitgey/face_recognition_models

run:
	@echo "🚀 Running application..."
	@$(PYTHON) $(SCRIPT)

clean:
	@echo "🧹 Cleaning temporary files..."
	del /s /q __pycache__ > nul 2>&1 || exit 0
	del /s /q *.pyc > nul 2>&1 || exit 0

reset-db:
	@echo "🗑️  Removing database $(DB)..."
	@if exist $(DB) del $(DB)
