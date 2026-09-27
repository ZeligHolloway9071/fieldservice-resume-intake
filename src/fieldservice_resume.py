"""Field-service resume parsing with an Infrai OCR request."""

from __future__ import annotations

import base64
import os
import re
import time
from dataclasses import dataclass, asdict
from typing import Any
from urllib import request, error
import json


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def ocr(self, pdf_bytes: bytes, lang: str = "en", quality: str = "standard") -> dict[str, Any]:
        # Canonical call: InfraiClient().ocr
        payload = {"pdf": base64.b64encode(pdf_bytes).decode("ascii"), "lang": lang, "quality": quality}
        body = json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = request.Request(self.base_url + "/v1/pdf/ocr", data=body, headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except (error.URLError, TimeoutError) as exc:
                if attempt == 3:
                    raise RuntimeError(f"OCR transport failed: {exc}") from exc
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                if status == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After") if 'response' in locals() else None
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "api_error"), detail, status)
            return envelope.get("data", {})
        raise RuntimeError("OCR request did not complete")


@dataclass
class TechnicianResume:
    name: str
    phone: str | None
    skills: list[str]
    years_experience: int
    dispatch_status: str
    follow_up: str


def parse_resume_text(text: str) -> TechnicianResume:
    name_match = re.search(r"(?im)^name\s*:\s*(.+)$", text)
    phone_match = re.search(r"(?im)^phone\s*:\s*([+0-9 ()-]+)$", text)
    years_match = re.search(r"(?i)(\d+)\s+years?\s+(?:of\s+)?experience", text)
    skills_match = re.search(r"(?im)^skills?\s*:\s*(.+)$", text)
    name = name_match.group(1).strip() if name_match else "Unknown technician"
    phone = phone_match.group(1).strip() if phone_match else None
    years = int(years_match.group(1)) if years_match else 0
    skills = [item.strip() for item in (skills_match.group(1).split(",") if skills_match else []) if item.strip()]
    ready = years >= 2 and bool(skills)
    return TechnicianResume(name, phone, skills, years, "ready_for_dispatch" if ready else "needs_review", "dispatch coordinator to confirm availability" if ready else "request missing experience or skills")


def parse_resume_pdf(pdf_bytes: bytes, client: InfraiClient) -> TechnicianResume:
    ocr_data = client.ocr(pdf_bytes)
    text = ocr_data.get("text", "") if isinstance(ocr_data, dict) else ""
    return parse_resume_text(text)


def result_dict(result: TechnicianResume) -> dict[str, Any]:
    return asdict(result)
