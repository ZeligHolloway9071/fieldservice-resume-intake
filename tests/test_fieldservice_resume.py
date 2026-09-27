import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fieldservice_resume import parse_resume_text


def test_experienced_technician_is_ready_for_dispatch():
    text = "Name: Maya Chen\nPhone: +1 555 0100\nSkills: HVAC, electrical\n5 years of experience"
    result = parse_resume_text(text)
    assert result.dispatch_status == "ready_for_dispatch"
    assert result.follow_up == "dispatch coordinator to confirm availability"
    assert result.skills == ["HVAC", "electrical"]
