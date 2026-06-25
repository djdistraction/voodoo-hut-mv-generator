#!/usr/bin/env python3
"""
Seed the WOW OH! series from the production guide.

This script imports the WOW_OH_Production_Shot_Sheet.xlsx into the database
as a canonical demo series with full shot manifest data and continuity rules.

Usage:
  cd backend
  python seed_wow_oh.py /path/to/WOW_OH_Production_Shot_Sheet.xlsx

This creates a "WOW OH!" series you can reference in new projects.
"""
import sys
import uuid
from pathlib import Path

def seed_series():
    """Create the WOW OH! series with full continuity bible and locked characters."""
    from database import db_create_series, db_update_series
    from config import settings

    series_id = str(uuid.uuid4())

    # Create series record
    series = db_create_series(
        series_id,
        name="WOW OH!",
        artist="HTXpunk",
    )

    # Continuity bible from the production document
    continuity_bible = {
        "core_concept": "Single continuous magical venue transformation",
        "visual_world": "A single nightclub venue that transforms from corporate nightmare (office) to liberating dance experience",
        "color_palette": ["poisonous green", "purple", "amber", "black", "hot pink"],
        "motion_style": "Dynamic cuts with Ken Burns parallax, glitch transitions for stress scenes",
        "transformation_logic": "As Mr. V's confidence grows, the venue shifts from corporate gray to vibrant neon",
        "office_nightmare_rules": [
            "Sharp geometric layouts for office/stress scenes",
            "Cold lighting in blues and grays",
            "Ominous background music/sound design",
            "Stress Monster as visible antagonist",
        ],
        "final_image": "Only Mr. V's glowing green eyes remain as the final frame",
        "banned_mistakes": [
            "No context switching (office props in club, or vice versa)",
            "Mr. V should never appear less confident as the song progresses",
            "No outdoor scenery (it's all one venue)",
            "No logos or text visible",
        ],
    }

    # Locked character definitions
    characters = {
        "Mr_V": {
            "role": "Protagonist",
            "description": "The main character discovering his power through dance",
            "visual_style": "Sharp, stylized, grows more confident",
            "states": ["stressed", "gaining_confidence", "fully_confident", "glowing_triumphant"],
        },
        "The_Dolls": {
            "role": "Background dancers",
            "description": "Stylized female dancers who evolve with the venue transformation",
        },
        "The_Boss_Stress_Monster": {
            "role": "Antagonist (stress)",
            "description": "Visible embodiment of workplace stress and anxiety",
        },
        "The_Band": {
            "role": "Musicians",
            "description": "Live band in the venue, energizing the space",
        },
        "The_Viewer": {
            "role": "POV observer",
            "description": "Camera often acts as the viewer experiencing the transformation",
        },
    }

    # Update series with continuity bible
    db_update_series(
        series_id,
        continuity_bible=continuity_bible,
        characters=characters,
        color_palette=continuity_bible["color_palette"],
        style_prompt="Psychedelic electronic music video with glitch aesthetic, neon colors, transformation narrative",
    )

    print(f"✓ Created WOW OH! series: {series_id}")
    print(f"  - Continuity bible locked with character definitions")
    print(f"  - Color palette: {', '.join(continuity_bible['color_palette'])}")
    print(f"  - Characters: {', '.join(characters.keys())}")
    return series_id


def import_shots(xlsx_path: str, series_id: str):
    """Import shot manifests from the Excel file."""
    from services.production_guide_importer import import_wow_oh_series
    from database import db_create_project, db_update_project, db_list_shot_manifests

    print(f"\n📋 Importing shots from: {xlsx_path}")

    parsed = import_wow_oh_series(series_id, xlsx_path)

    print(f"✓ Imported {len(parsed['shots'])} shots:")
    for shot in parsed['shots'][:5]:
        print(f"  - Shot {shot['shot_number']}: {shot['audio_cue'][:40]}")
    if len(parsed['shots']) > 5:
        print(f"  ... and {len(parsed['shots'] - 5} more")

    # Optional: create a demo project with these shots
    demo_project_id = str(uuid.uuid4())
    db_create_project(demo_project_id, "WOW OH! Preview", "HTXpunk")
    db_update_project(demo_project_id, series_id=series_id)

    # Create shot manifests for the demo project
    from services.production_guide_importer import create_project_shot_manifests
    manifest_ids = create_project_shot_manifests(demo_project_id, parsed['shots'])

    db_update_project(
        demo_project_id,
        stage="awaiting_manifest_approval",
        revision_notes="Seeded from WOW OH! production guide",
    )

    print(f"\n✓ Created demo project {demo_project_id}")
    print(f"  - Status: awaiting_manifest_approval (ready for review)")
    print(f"  - Shots: {len(manifest_ids)} manifests created")

    print(f"\n📝 Production Guide Metadata:")
    for key, value in parsed['metadata'].items():
        print(f"  - {key}: {value}")

    return demo_project_id


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    xlsx_path = sys.argv[1]
    if not Path(xlsx_path).exists():
        print(f"❌ File not found: {xlsx_path}")
        sys.exit(1)

    print("=" * 60)
    print("WOW OH! Production Guide Seeder")
    print("=" * 60)

    try:
        # Ensure DB is initialized
        import asyncio
        from database import init_db
        asyncio.run(init_db())

        series_id = seed_series()
        project_id = import_shots(xlsx_path, series_id)

        print("\n" + "=" * 60)
        print("✅ Seeding complete!")
        print("\nNext steps:")
        print(f"  1. Start the frontend: cd ../frontend && npm run dev")
        print(f"  2. Go to http://localhost:3000")
        print(f"  3. Find project '{project_id}'")
        print(f"  4. Review and approve the production plan")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
