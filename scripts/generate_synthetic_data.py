"""Generate CLEARLY LABELLED synthetic test data in samples/synthetic_input/.

This data is invented for testing the pipeline only. Every chat name, sender and image carries a
SYNTHETIC label, CSP IDs use the SYN prefix, and it is written outside input/ so it can never be
mixed into the real report.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples" / "synthetic_input"


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def screenshot(path: Path, lines: list[str], tint=(232, 240, 254)) -> None:
    """A phone-sized mock of an app screen with a SYNTHETIC watermark."""
    img = Image.new("RGB", (720, 1280), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 720, 110], fill=(31, 56, 100))
    d.text((30, 35), "SBI CSP Visit (SYNTHETIC MOCK)", fill="white", font=_font(34))
    d.rectangle([30, 160, 690, 760], fill=tint, outline=(150, 150, 150))
    y = 190
    for line in lines:
        d.text((60, y), line, fill=(20, 20, 20), font=_font(32))
        y += 64
    d.text((60, 1150), "SYNTHETIC TEST IMAGE - NOT REAL", fill=(192, 0, 0), font=_font(36))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=90)


def unrelated_photo(path: Path) -> None:
    img = Image.new("RGB", (800, 600), (120, 160, 110))
    d = ImageDraw.Draw(img)
    d.ellipse([250, 150, 550, 450], fill=(230, 200, 90))
    d.text((40, 540), "SYNTHETIC unrelated photo", fill="white", font=_font(28))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=90)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    # --- Group 1: Android export (dd/mm/yyyy, 12h) --------------------------------------------
    g1 = OUT / "WhatsApp Chat with [SYNTHETIC] Bihar DC Team"
    screenshot(g1 / "IMG-20260922-WA0001.jpg", ["Visit could not be marked", "Your location is 827 m away",
                                                "from the CSP location.", "Allowed radius: 100 m",
                                                "Current location: 25.6093, 85.1376",
                                                "Planned location: 25.6150, 85.1410"])
    screenshot(g1 / "IMG-20260924-WA0002.jpg", ["Location mismatch", "Planned: Village Sonpur",
                                                "Actual: 2.3 km away"], tint=(255, 236, 220))
    screenshot(g1 / "IMG-20260924-WA0003.jpg", ["Unable to fetch location", "Please enable GPS", "and try again"])
    shutil.copy(g1 / "IMG-20260922-WA0001.jpg", g1 / "IMG-20260925-WA0004.jpg")  # same screenshot re-sent
    unrelated_photo(g1 / "IMG-20260929-WA0005.jpg")
    screenshot(g1 / "IMG-20261001-WA0006.jpg", ["Location refresh failed", "Server error 500", "Try again later"])

    lines = [
        "20/09/2026, 9:00 am - Messages and calls are end-to-end encrypted. No one outside of this chat can read them.",
        "20/09/2026, 9:05 am - Test DC Asha (SYNTHETIC): CSP ID: SYN10011 location 300 m away aa raha hai (before reporting period)",
        "22/09/2026, 10:15 am - Test DC Asha (SYNTHETIC): CSP ID: SYN10001 visit pe location 827 m away dikha raha hai, visit submit nahi ho raha. District: Patna",
        "22/09/2026, 10:15 am - Test DC Asha (SYNTHETIC): IMG-20260922-WA0001.jpg (file attached)",
        "22/09/2026, 11:02 am - Test FO Ravi (SYNTHETIC): GPS location not detected at kiosk, CSP ID SYN10002, Dist: Gaya",
        "22/09/2026, 11:30 am - Test Manager Kiran (SYNTHETIC): Please share CSP ID and district with every location issue.",
        "23/09/2026, 2:40 pm - Test DC Asha (SYNTHETIC): CSP ID: SYN10001 location issue resolved, visit ho gaya",
        "24/09/2026, 9:05 am - Test FO Ravi (SYNTHETIC): IMG-20260924-WA0002.jpg (file attached)",
        "24/09/2026, 9:05 am - Test FO Ravi (SYNTHETIC): IMG-20260924-WA0003.jpg (file attached)",
        "24/09/2026, 9:06 am - Test FO Ravi (SYNTHETIC): Location mismatch - planned location alag hai,",
        "CSP ID: SYN10003, District: Nalanda, Village: Sonpur",
        "24/09/2026, 9:40 am - +91 98765 43210: refresh location button not working, visit update nahi ho raha CSP ID SYN10004 District: Patna",
        "25/09/2026, 4:10 pm - Test DC Meena (SYNTHETIC): IMG-20260925-WA0004.jpg (file attached)",
        "same issue again 827 m away, CSP ID: SYN10001",
        "26/09/2026, 12:20 pm - Test DC Meena (SYNTHETIC): लोकेशन नहीं आ रहा है, CSP ID: SYN10005, जिला: Muzaffarpur",
        "27/09/2026, 10:00 am - Test FO Ravi (SYNTHETIC): <Media omitted>",
        "27/09/2026, 10:01 am - Test FO Ravi (SYNTHETIC): Lat long galat aa raha hai CSP ID: SYN10006",
        "28/09/2026, 6:45 pm - Test DC Asha (SYNTHETIC): IMG-20260928-WA0009.jpg (file attached)",
        "Server error aa raha hai visit submit karte time CSP ID: SYN10007",
        "29/09/2026, 8:00 am - Test Manager Kiran (SYNTHETIC): Good morning team",
        "29/09/2026, 8:02 am - Test Manager Kiran (SYNTHETIC): IMG-20260929-WA0005.jpg (file attached)",
        "30/09/2026, 3:15 pm - Test DC Meena (SYNTHETIC): CSP ID: SYN10008 location 1.2 km door bata raha hai, radius 100m hai. District: Vaishali",
        "01/10/2026, 11:11 am - Test DC Asha (SYNTHETIC): IMG-20261001-WA0006.jpg (file attached)",
        "01/10/2026, 11:12 am - Test DC Asha (SYNTHETIC): Current location: 25.6093, 85.1376 Planned location: 25.6150, 85.1410 CSP ID: SYN10009 refresh karne pe bhi update nahi hua",
        "03/10/2026, 5:30 pm - Test FO Ravi (SYNTHETIC): All CSP visits done today, no issues",
    ]
    g1.mkdir(parents=True, exist_ok=True)
    (g1 / "WhatsApp Chat with [SYNTHETIC] Bihar DC Team.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- Group 2: iOS export, zipped (dd/mm/yy, 24h with seconds) ------------------------------
    g2 = OUT / "_build_ios"
    screenshot(g2 / "00000007-PHOTO-2026-10-02-14-20-05.jpg", ["You are 450 m away", "from planned location"])
    ios = [
        "[02/10/26, 14:18:40] Test DC Neha (SYNTHETIC): Messages and calls are end-to-end encrypted.",
        "[02/10/26, 14:20:05] Test DC Neha (SYNTHETIC): ‎<attached: 00000007-PHOTO-2026-10-02-14-20-05.jpg>",
        "[02/10/26, 14:20:31] Test DC Neha (SYNTHETIC): CSP ID: SYN20001 distance 450 m dikha raha hai, visit pending. District: Lucknow",
        "[05/10/26, 09:12:00] Test FO Arjun (SYNTHETIC): GPS location not detected at kiosk, CSP ID SYN10002, Dist: Gaya",
        "[07/10/26, 16:45:10] Test FO Arjun (SYNTHETIC): App crash ho raha hai visit ke time, CSP ID: SYN20002 District: Kanpur",
        "[09/10/26, 10:05:00] Test DC Neha (SYNTHETIC): CSP ID: SYN20001 abhi bhi 450 m away aa raha hai, escalate kariye",
    ]
    (g2 / "_chat.txt").write_text("\n".join(ios) + "\n", encoding="utf-8")
    import zipfile
    zpath = OUT / "WhatsApp Chat - [SYNTHETIC] UP Field Team.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        for f in g2.iterdir():
            zf.write(f, f.name)
    shutil.rmtree(g2)  # the parser names "_chat.txt" after the zip, as WhatsApp iOS exports do

    # --- Messages copied from WhatsApp Web (text only) --------------------------------------
    web = OUT / "copied_from_whatsapp_web"
    web.mkdir(parents=True)
    (web / "[SYNTHETIC] Jharkhand Ops copied.txt").write_text(
        "[3:20 pm, 13/10/2026] Test DC Meena (SYNTHETIC): GPS signal weak, location fetch nahi ho rahi CSP ID: SYN10010 Dist: Ranchi\n"
        "[3:41 pm, 13/10/2026] Test DC Meena (SYNTHETIC): Same issue, update location fail ho raha hai\n",
        encoding="utf-8")

    # --- An image with no chat export (image-only input) ----------------------------------------
    screenshot(OUT / "loose_images" / "WhatsApp Image 2026-10-04 at 12.30.15.jpeg",
               ["Location not detected", "Turn on GPS"])
    (OUT / "README_SYNTHETIC.md").write_text(
        "SYNTHETIC TEST DATA. Everything in this folder was generated by scripts/generate_synthetic_data.py\n"
        "for testing. It is not real WhatsApp evidence and must never be reported as such.\n", encoding="utf-8")
    print(f"Synthetic test data written to {OUT}")


if __name__ == "__main__":
    main()
