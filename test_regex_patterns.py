"""
Test regex patterns
"""
import re

sparql = """PREFIX sh: <http://dhia.org/ontologies/smarthealth#>

INSERT DATA {
  sh:Breakfast_test_waffles a sh:Breakfast ;
    sh:name "test_waffles" ;
    sh:calories 350 .
}
"""

print("Testing SPARQL:")
print(sparql)
print("\n" + "="*70)

# Test each pattern
patterns = {
    "Pattern 3 (OLD)": r'sh:Meal_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)\s*;\s*sh:calories\s+(\d+)\s*;\s*sh:name\s+"([^"]+)"',
    "Pattern 3 (NEW)": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)\s*;\s*sh:calories\s+(\d+)\s*;\s*sh:name\s+"([^"]+)"',
    "Pattern 4 (OLD)": r'sh:Meal_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:calories\s+(\d+)[^}]*sh:name\s+"([^"]+)"',
    "Pattern 4 (NEW)": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:calories\s+(\d+)[^}]*sh:name\s+"([^"]+)"',
    "Pattern 5 (OLD)": r'sh:Meal_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name\s+"([^"]+)"[^}]*sh:calories\s+(\d+)',
    "Pattern 5 (NEW)": r'sh:(?:Meal|Breakfast|Lunch|Dinner|Snack)_\w+\s+a\s+sh:(Breakfast|Lunch|Dinner|Snack)[^}]*sh:name\s+"([^"]+)"[^}]*sh:calories\s+(\d+)',
}

for name, pattern in patterns.items():
    match = re.search(pattern, sparql, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"✅ {name} MATCHED!")
        print(f"   Groups: {match.groups()}")
    else:
        print(f"❌ {name} - No match")

print("\n" + "="*70)
print("Testing with single line version:")
sparql_oneline = """sh:Breakfast_test_waffles a sh:Breakfast ; sh:name "test_waffles" ; sh:calories 350 ."""
print(sparql_oneline)
print()

for name, pattern in patterns.items():
    match = re.search(pattern, sparql_oneline, re.IGNORECASE | re.DOTALL)
    if match:
        print(f"✅ {name} MATCHED!")
        print(f"   Groups: {match.groups()}")
    else:
        print(f"❌ {name} - No match")
