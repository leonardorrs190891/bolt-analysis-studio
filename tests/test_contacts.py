"""Test script for contact system."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bolt_analysis_studio.core.contacts import (
    ContactFactory,
    create_api_6a_joint_config,
    create_asme_b16_5_joint_config,
    create_vdi_2230_joint_config,
)

# Test 1: API 6A Joint with RTJ gasket
print("=" * 60)
print("TEST 1: API 6A Joint with RTJ Gasket")
print("=" * 60)
config_api = create_api_6a_joint_config('M20', '5K', 'RTJ')
factory_api = ContactFactory()
contacts_api = factory_api.create_complete_joint(config_api)
print(f"Created {len(contacts_api)} contacts:")
for c in contacts_api:
    print(f"  - {c.id}: {c.type}")
print()

# Test 2: ASME B16.5 Joint with spiral wound gasket
print("=" * 60)
print("TEST 2: ASME B16.5 Joint with Spiral Wound Gasket")
print("=" * 60)
config_asme = create_asme_b16_5_joint_config('M20', '150', True)
factory_asme = ContactFactory()
contacts_asme = factory_asme.create_complete_joint(config_asme)
print(f"Created {len(contacts_asme)} contacts:")
for c in contacts_asme:
    print(f"  - {c.id}: {c.type}")
print()

# Test 3: VDI 2230 Joint with Belleville washers
print("=" * 60)
print("TEST 3: VDI 2230 Joint with Belleville Washers")
print("=" * 60)
config_vdi = create_vdi_2230_joint_config('M20', True)
factory_vdi = ContactFactory()
contacts_vdi = factory_vdi.create_complete_joint(config_vdi)
print(f"Created {len(contacts_vdi)} contacts:")
for c in contacts_vdi:
    print(f"  - {c.id}: {c.type}")
print()

# Test DOF validation
print("=" * 60)
print("TEST 4: DOF Validation")
print("=" * 60)
n_dof = 14
is_valid, errors = factory_api.validate_dof_mapping(n_dof)
print(f"DOF Validation (n_dof={n_dof}): {'PASS' if is_valid else 'FAIL'}")
if errors:
    for error in errors:
        print(f"  ERROR: {error}")
else:
    print("  All DOFs within valid range")
print()

# Test summary
print("=" * 60)
print("TEST 5: Contact System Summary")
print("=" * 60)
summary = factory_api.get_summary()
print(f"Total contacts: {summary['total_contacts']}")
print("Contact types:")
for contact_type, count in summary['contact_types'].items():
    print(f"  - {contact_type}: {count}")
print()

print("=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 60)
