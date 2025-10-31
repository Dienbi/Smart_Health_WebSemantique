#!/usr/bin/env python
"""
Setup script for Smart Health Web project
Run this script to perform initial project setup
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and print the result"""
    print(f"\n{'='*60}")
    print(f"⚙️  {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {description} failed!")
        return False
    
    print(f"✅ {description} completed successfully!")
    return True


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🏥 Smart Health Web - Project Setup")
    print("="*60)
    
    # Check if we're in the correct directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        sys.exit(1)
    
    # Create superuser
    print("\n" + "="*60)
    print("👤 Create Superuser Account")
    print("="*60)
    print("Please create an admin account for Django admin panel:")
    subprocess.run("python manage.py createsuperuser", shell=True)
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Set up Apache Fuseki server")
    print("2. Upload ontology file (ontology/smarthealth.ttl) to Fuseki")
    print("3. Configure .env file with your settings")
    print("4. Run the server: python manage.py runserver")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
