#!/usr/bin/env python
r"""
Simple smoke test to verify all Defi routes and basic functionality.
Run with: .venv\Scripts\python.exe test_smoke.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Health.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from apps.defis.models import Defi, DefiObjectif, Participation
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def print_test(name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   → {message}")

@override_settings(ALLOWED_HOSTS=['localhost', '127.0.0.1', 'testserver'])
def main():
    print("\n" + "="*60)
    print("SMOKE TEST: Defi Module (Front & Back)")
    print("="*60 + "\n")

    client = Client()

    # Create test user
    print("📝 Setting up test data...")
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': False}
    )
    user.set_password('testpass123')
    user.save()

    staff_user, _ = User.objects.get_or_create(
        username='staffuser',
        defaults={'email': 'staff@example.com', 'is_staff': True}
    )
    staff_user.set_password('staffpass123')
    staff_user.save()

    # Create test defi
    defi = Defi.objects.create(
        defi_name="Test Challenge",
        defi_description="A test challenge for smoke testing"
    )
    # Create objectives
    obj = DefiObjectif.objects.create(
        defi=defi,
        description="Test Objective",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30)
    )
    print(f"✓ Created test defi: {defi.defi_name} (ID: {defi.defi_id})")
    print(f"✓ Created test objective: {obj.description}\n")

    # Test 1: Front list view (anonymous)
    response = client.get('/challenges/')
    print_test("Front list view (anonymous)", response.status_code == 200, f"Status: {response.status_code}")

    # Test 2: Front detail view (anonymous)
    response = client.get(f'/challenges/{defi.defi_id}/')
    print_test("Front detail view (anonymous)", response.status_code == 200, f"Status: {response.status_code}")

    # Test 3: Join defi (not logged in - should redirect)
    response = client.post(f'/challenges/{defi.defi_id}/join/', follow=False)
    print_test("Join defi (not logged in)", response.status_code == 302, f"Should redirect (302), got {response.status_code}")

    # Login as regular user
    print("\n🔐 Logging in as testuser...")
    client.login(username='testuser', password='testpass123')

    # Test 4: Join defi (logged in)
    response = client.post(f'/challenges/{defi.defi_id}/join/', follow=True)
    participation = Participation.objects.filter(user=user, defi=defi).first()
    print_test("Join defi (logged in)", participation is not None, f"Participation created: {participation is not None}")

    # Test 5: Front detail view after join
    response = client.get(f'/challenges/{defi.defi_id}/')
    print_test("Front detail view (after join)", response.status_code == 200, f"Status: {response.status_code}")

    # Test 6: Update progress
    response = client.post(
        f'/challenges/{defi.defi_id}/update-progress/',
        {'progress_value': '50'},
        follow=True
    )
    if participation:
        participation.refresh_from_db()
        progress_value = participation.progress.progress_value if participation.progress else None
        print_test("Update progress", progress_value == 50, f"Progress value: {progress_value}")
    else:
        print_test("Update progress", False, "No participation found")

    # Test 7: Leave defi
    if participation:
        response = client.post(f'/challenges/{defi.defi_id}/leave/', follow=True)
        participation.refresh_from_db()
        left = participation.end_date is not None
        print_test("Leave defi", left, f"Participation ended: {left}")

    # Logout and login as staff
    print("\n🔐 Logging in as staffuser...")
    client.logout()
    client.login(username='staffuser', password='staffpass123')

    # Test 8: Admin list view
    response = client.get('/backoffice/defis/')
    print_test("Admin list view", response.status_code == 200, f"Status: {response.status_code}")

    # Test 9: Admin detail view
    response = client.get(f'/backoffice/defis/{defi.defi_id}/')
    print_test("Admin detail view", response.status_code == 200, f"Status: {response.status_code}")

    # Test 10: Admin create page
    response = client.get('/backoffice/defis/create/')
    print_test("Admin create page", response.status_code == 200, f"Status: {response.status_code}")

    # Test 11: Admin create defi
    response = client.post(
        '/backoffice/defis/create/',
        {
            'defi_name': 'New Admin Defi',
            'defi_description': 'Created via admin',
            'badge_gold': 'on',
            'badge_silver': 'on',
            'status_in_progress': 'on',
            'objectives-TOTAL_FORMS': '1',
            'objectives-INITIAL_FORMS': '0',
            'objectives-MIN_NUM_FORMS': '0',
            'objectives-MAX_NUM_FORMS': '1000',
        },
        follow=True
    )
    new_defi = Defi.objects.filter(defi_name='New Admin Defi').first()
    print_test("Admin create defi", new_defi is not None, f"New defi created: {new_defi is not None}")

    # Test 12: Admin edit page
    response = client.get(f'/backoffice/defis/{defi.defi_id}/edit/')
    print_test("Admin edit page", response.status_code == 200, f"Status: {response.status_code}")

    # Test 13: API - list defis
    response = client.get('/challenges/api/defis/')
    print_test("API list defis", response.status_code == 200, f"Status: {response.status_code}")

    print("\n" + "="*60)
    print("SMOKE TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
