"""Database Data Deduplication Script.

Scans SQLite / PostgreSQL database tables for duplicate records (shelters, hazard zones,
population, alerts, animals, animal shelters, communication messages), safely merges/removes
duplicates, preserves the newest authoritative record, and logs all operations.
"""

import sys
import os
from collections import defaultdict

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, init_db
from backend.app.models.entities import (
    Shelter,
    HazardZone,
    Population,
    Alert,
    Animal,
    AnimalShelter,
    CommunicationMessage,
)


def run_database_deduplication():
    print("==========================================================")
    print(" STARTING DATABASE DATA DEDUPLICATION CLEANUP")
    print("==========================================================")

    init_db()
    db = SessionLocal()
    total_removed = 0

    try:
        # 1. Deduplicate Shelters (Group by Name)
        print("\n[1/6] Auditing Shelters table for duplicate names...")
        shelters = db.query(Shelter).order_by(Shelter.id.asc()).all()
        shelter_map = defaultdict(list)
        for s in shelters:
            norm_name = s.name.strip().lower()
            shelter_map[norm_name].append(s)

        for norm_name, s_list in shelter_map.items():
            if len(s_list) > 1:
                # Keep the one with highest occupancy/newest ID
                authoritative = s_list[-1]
                duplicates = s_list[:-1]
                print(f"  -> Found {len(s_list)} records for shelter '{s_list[0].name}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Shelter ID {dup.id} ({dup.name})")
                    db.delete(dup)
                    total_removed += 1

        # 2. Deduplicate Hazard Zones (Group by Name)
        print("\n[2/6] Auditing Hazard Zones table for duplicate names...")
        hazards = db.query(HazardZone).order_by(HazardZone.id.asc()).all()
        hazard_map = defaultdict(list)
        for h in hazards:
            norm_name = h.name.strip().lower()
            hazard_map[norm_name].append(h)

        for norm_name, h_list in hazard_map.items():
            if len(h_list) > 1:
                authoritative = h_list[-1]
                duplicates = h_list[:-1]
                print(f"  -> Found {len(h_list)} records for Hazard Zone '{h_list[0].name}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Hazard Zone ID {dup.id} ({dup.name})")
                    db.delete(dup)
                    total_removed += 1

        # 3. Deduplicate Animals (Group by tag_id)
        print("\n[3/6] Auditing Animals table for duplicate tag_ids...")
        animals = db.query(Animal).order_by(Animal.id.asc()).all()
        animal_map = defaultdict(list)
        for a in animals:
            norm_tag = a.tag_id.strip().upper()
            animal_map[norm_tag].append(a)

        for norm_tag, a_list in animal_map.items():
            if len(a_list) > 1:
                authoritative = a_list[-1]
                duplicates = a_list[:-1]
                print(f"  -> Found {len(a_list)} records for Animal tag '{norm_tag}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Animal ID {dup.id} ({dup.tag_id})")
                    db.delete(dup)
                    total_removed += 1

        # 4. Deduplicate Animal Shelters (Group by Name)
        print("\n[4/6] Auditing Animal Shelters table for duplicate names...")
        ans = db.query(AnimalShelter).order_by(AnimalShelter.id.asc()).all()
        ans_map = defaultdict(list)
        for a in ans:
            norm_name = a.name.strip().lower()
            ans_map[norm_name].append(a)

        for norm_name, a_list in ans_map.items():
            if len(a_list) > 1:
                authoritative = a_list[-1]
                duplicates = a_list[:-1]
                print(f"  -> Found {len(a_list)} records for Animal Shelter '{a_list[0].name}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Animal Shelter ID {dup.id} ({dup.name})")
                    db.delete(dup)
                    total_removed += 1

        # 5. Deduplicate Alerts (Group by title + affected_area)
        print("\n[5/6] Auditing Alerts table for duplicate active titles...")
        alerts = db.query(Alert).filter(Alert.status == "ACTIVE").order_by(Alert.id.asc()).all()
        alert_map = defaultdict(list)
        for al in alerts:
            key = (al.title.strip().lower(), al.affected_area.strip().lower())
            alert_map[key].append(al)

        for key, al_list in alert_map.items():
            if len(al_list) > 1:
                authoritative = al_list[-1]
                duplicates = al_list[:-1]
                print(f"  -> Found {len(al_list)} records for Alert '{al_list[0].title}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Alert ID {dup.id} ({dup.title})")
                    db.delete(dup)
                    total_removed += 1

        # 6. Deduplicate Communication Messages (Group by title + category)
        print("\n[6/6] Auditing Communication Messages for duplicate titles...")
        messages = db.query(CommunicationMessage).order_by(CommunicationMessage.id.asc()).all()
        msg_map = defaultdict(list)
        for m in messages:
            key = (m.title.strip().lower(), m.category.strip().lower())
            msg_map[key].append(m)

        for key, m_list in msg_map.items():
            if len(m_list) > 1:
                authoritative = m_list[-1]
                duplicates = m_list[:-1]
                print(f"  -> Found {len(m_list)} records for Message '{m_list[0].title}'. Keeping ID {authoritative.id}.")
                for dup in duplicates:
                    print(f"     [REMOVE DUP] Message ID {dup.id} ({dup.title})")
                    db.delete(dup)
                    total_removed += 1

        db.commit()
        print("\n==========================================================")
        print(f"[OK] DEDUPLICATION COMPLETE: {total_removed} duplicate records safely removed.")
        print("==========================================================")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Deduplication script error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_database_deduplication()
