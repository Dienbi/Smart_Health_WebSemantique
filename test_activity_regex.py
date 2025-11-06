"""
Test activity pattern matching
"""
import re

sparql_query = """PREFIX sh: <http://dhia.org/ontologies/smarthealth#>
INSERT DATA { sh:Cardio_jogging a sh:Cardio ; sh:activity_name "jogging" }"""

activity_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+\s+a\s+sh:(Cardio|Musculation|Natation)[^}]*sh:activity_name\s+"([^"]+)"'

print("=" * 80)
print("Testing Activity Pattern Match")
print("=" * 80)
print(f"\nSPARQL:\n{sparql_query}")
print(f"\nPattern:\n{activity_pattern}")
print("\n" + "=" * 80)

match = re.search(activity_pattern, sparql_query, re.IGNORECASE | re.DOTALL)

if match:
    print("✅ MATCH FOUND!")
    print(f"   Group 1 (Type): {match.group(1)}")
    print(f"   Group 2 (Name): {match.group(2)}")
    print(f"   Full match: {match.group(0)}")
else:
    print("❌ NO MATCH")
    
    # Debug - try parts
    print("\nDEBUG - Testing parts:")
    
    # Test identifier
    id_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+'
    id_match = re.search(id_pattern, sparql_query)
    print(f"  ID pattern: {'✅ ' + id_match.group() if id_match else '❌ No match'}")
    
    # Test type
    type_pattern = r'a\s+sh:(Cardio|Musculation|Natation)'
    type_match = re.search(type_pattern, sparql_query)
    print(f"  Type pattern: {'✅ ' + type_match.group(1) if type_match else '❌ No match'}")
    
    # Test name
    name_pattern = r'sh:activity_name\s+"([^"]+)"'
    name_match = re.search(name_pattern, sparql_query)
    print(f"  Name pattern: {'✅ ' + name_match.group(1) if name_match else '❌ No match'}")
    
    # Test the problematic [^}]* part
    print("\n  Testing [^}]* part:")
    partial_pattern = r'sh:Cardio_\w+\s+a\s+sh:Cardio\s+;'
    partial_match = re.search(partial_pattern, sparql_query)
    print(f"    With semicolon: {'✅ Match' if partial_match else '❌ No match'}")
    
    # The issue might be [^}]* doesn't match the semicolon and space properly
    # Let's try a more flexible pattern
    flexible_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+\s+a\s+sh:(Cardio|Musculation|Natation).*?sh:activity_name\s+"([^"]+)"'
    flexible_match = re.search(flexible_pattern, sparql_query, re.DOTALL)
    print(f"  Flexible pattern (.*?): {'✅ Match' if flexible_match else '❌ No match'}")
    
print("=" * 80)
