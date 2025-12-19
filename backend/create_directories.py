# Databricks notebook source
"""
Create all necessary directories for the application
"""

import os

# Directories to create
directories = [
    'data',
    'uploads',
    'chroma_db',
    'models',
    'logs',
    'docs'
]

print("📁 Creating necessary directories...\n")

for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ Failed to create {directory}/")
    except Exception as e:
        print(f"❌ Error creating {directory}/: {e}")

print("\n🎉 All directories created!")