"""
Test the regex pattern against the generated SPARQL
"""
import re

# The pattern from views.py
activity_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+\s+a\s+sh:(Cardio|Musculation|Natation)[^}]*sh:activity_name\s+"([^"]+)"'

# Test SPARQL queries from AI
test_queries = [
    'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Cardio_jogging a sh:Cardio ; sh:activity_name "jogging" }',
    'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Musculation_benchpress a sh:Musculation ; sh:activity_name "bench press" }',
    'PREFIX sh: <http://dhia.org/ontologies/smarthealth#>\n\nINSERT DATA { sh:Natation_swimming a sh:Natation ; sh:activity_name "swimming" }',
]

print("=" * 80)
print("Testing Activity Pattern Matching")
print("=" * 80)
print(f"\nPattern: {activity_pattern}\n")

for i, query in enumerate(test_queries, 1):
    print(f"\n{'=' * 80}")
    print(f"Test {i}:")
    print(f"Query: {query}")
    print("-" * 80)
    
    match = re.search(activity_pattern, query, re.IGNORECASE | re.DOTALL)
    
    if match:
        print(f"✅ MATCH FOUND!")
        print(f"   Activity Type: {match.group(1)}")
        print(f"   Activity Name: {match.group(2)}")
    else:
        print(f"❌ NO MATCH!")
        
        # Try to debug why
        simple_pattern = r'sh:(?:Activity|Cardio|Musculation|Natation)_\w+'
        simple_match = re.search(simple_pattern, query)
        if simple_match:
            print(f"   ✓ Found activity identifier: {simple_match.group()}")
        else:
            print(f"   ✗ Could not find activity identifier")
            
        type_pattern = r'a\s+sh:(Cardio|Musculation|Natation)'
        type_match = re.search(type_pattern, query)
        if type_match:
            print(f"   ✓ Found type: {type_match.group(1)}")
        else:
            print(f"   ✗ Could not find type")
            
        name_pattern = r'sh:activity_name\s+"([^"]+)"'
        name_match = re.search(name_pattern, query)
        if name_match:
            print(f"   ✓ Found name: {name_match.group(1)}")
        else:
            print(f"   ✗ Could not find name")

print(f"\n{'=' * 80}")
print("Test completed!")
print("=" * 80)
