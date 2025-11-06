"""Test exact SPARQL from logs"""
import re

sparql = """PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
    sh:Breakfast_test a sh:Breakfast ; sh:name "test" ; sh:calories 0 .
}"""

print("Testing SPARQL:")
print(sparql)
print("\n" + "="*70 + "\n")

# All 5 patterns from views.py
patterns = {
    "Pattern 1": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:meal_name\s+"([^"]+)"[^}]*sh:total_calories\s+(\d+)',
    "Pattern 2": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name_meal\s+"([^"]+)"[^}]*sh:calories_total\s+(\d+)',
    "Pattern 3": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)\s*;\s*sh:calories\s+(\d+)\s*;\s*sh:name\s+"([^"]+)"',
    "Pattern 4": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:calories\s+(\d+)[^}]*sh:name\s+"([^"]+)"',
    "Pattern 5": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name\s+"([^"]+)"[^}]*sh:calories\s+(\d+)',
}

# Test new pattern with exact semicolon matching
patterns["Pattern 6 (NEW)"] = r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)\s*;\s*sh:name\s+"([^"]+)"\s*;\s*sh:calories\s+(\d+)'

for name, pattern in patterns.items():
    match = re.search(pattern, sparql, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"✅ {name} MATCHED!")
        print(f"   Groups: {match.groups()}")
    else:
        print(f"❌ {name} - No match")

print("\n" + "="*70)
print("ANALYSIS:")
print("Pattern 3 expects: calories THEN name")
print("Pattern 5 expects: name THEN calories (with [^}] between)")
print("Pattern 6 expects: name THEN calories (with explicit semicolons)")
print("="*70)
