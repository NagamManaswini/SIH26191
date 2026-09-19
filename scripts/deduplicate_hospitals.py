"""Hospital Data Deduplication Script.

Detects, logs, and safely merges duplicate hospital records based on:
1. Identical hospital_id
2. Matching hospital name (case-insensitive) and geographic coordinates (tolerance: ~100 meters)

Preserves audit history and capacity records before deactivating/deleting duplicate entries.
"""

import sys
import os
import math
from typing import List, Dict, Tuple

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.entities import Hospital, HospitalCapacity, HospitalUpdate


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two lat/lon coordinates."""
    R = 6371000.0  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def deduplicate_hospitals():
    db = SessionLocal()
    print("=" * 60)
    print("🏥 HOSPITAL DATA DEDUPLICATION SYSTEM")
    print("=" * 60)

    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    print(f"Total active hospital records analyzed: {len(hospitals)}")

    duplicates_found: List[Tuple[Hospital, Hospital]] = []
    seen_ids = set()

    for i in range(len(hospitals)):
        h1 = hospitals[i]
        if h1.id in seen_ids:
            continue

        for j in range(i + 1, len(hospitals)):
            h2 = hospitals[j]
            if h2.id in seen_ids:
                continue

            is_dup = False
            reason = ""

            # Check 1: Same hospital_id
            if h1.hospital_id.strip().lower() == h2.hospital_id.strip().lower():
                is_dup = True
                reason = f"Identical Hospital ID: '{h1.hospital_id}'"

            # Check 2: Same name & near coordinates (< 100m)
            elif h1.name.strip().lower() == h2.name.strip().lower():
                dist_m = haversine_distance(h1.latitude, h1.longitude, h2.latitude, h2.longitude)
                if dist_m <= 150.0:
                    is_dup = True
                    reason = f"Matching Name '{h1.name}' & Proximity {dist_m:.1f}m"

            if is_dup:
                duplicates_found.append((h1, h2, reason))
                seen_ids.add(h2.id)

    if not duplicates_found:
        print("\n✅ Zero duplicate hospital records detected. Database is clean!")
        print("=" * 60)
        db.close()
        return

    print(f"\n⚠️ Detected {len(duplicates_found)} duplicate hospital pair(s):")
    merged_count = 0

    for keeper, duplicate, reason in duplicates_found:
        print(f"\n--- DUPLICATE PAIR ---")
        print(f"Reason: {reason}")
        print(f"Keep Primary ID: [{keeper.id}] {keeper.name} ({keeper.hospital_id}) - {keeper.district}")
        print(f"Merge Duplicate ID: [{duplicate.id}] {duplicate.name} ({duplicate.hospital_id}) - {duplicate.district}")

        # Preserve historical capacity if keeper lacks capacity
        if not keeper.capacity and duplicate.capacity:
            dup_cap = duplicate.capacity
            dup_cap.hospital_id = keeper.id
            db.add(dup_cap)
            print(f"  -> Transferred capacity data to primary record {keeper.id}")

        # Transfer audit logs from duplicate to keeper
        updates = db.query(HospitalUpdate).filter(HospitalUpdate.hospital_id == duplicate.id).all()
        for u in updates:
            u.hospital_id = keeper.id
            db.add(u)
        if updates:
            print(f"  -> Re-assigned {len(updates)} capacity audit logs to primary record {keeper.id}")

        # Log deduplication audit entry
        dedup_log = HospitalUpdate(
            hospital_id=keeper.id,
            field_name="deduplication_merge",
            old_value=f"Duplicate ID {duplicate.id} ({duplicate.hospital_id})",
            new_value=f"Merged into Primary ID {keeper.id}",
            updated_by="Deduplication Engine",
        )
        db.add(dedup_log)

        # Deactivate duplicate record safely
        duplicate.is_active = False
        duplicate.name = f"{duplicate.name} [MERGED DUP {duplicate.id}]"
        merged_count += 1

    db.commit()
    print("\n" + "=" * 60)
    print(f"🎉 Deduplication successfully completed! Merged {merged_count} duplicate record(s).")
    print("=" * 60)
    db.close()


if __name__ == "__main__":
    deduplicate_hospitals()
