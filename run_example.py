import json
import sys

from src.fieldservice_resume import InfraiClient, parse_resume_pdf, result_dict


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python run_example.py resume.pdf")
    result = parse_resume_pdf(open(sys.argv[1], "rb").read(), InfraiClient())
    print(json.dumps(result_dict(result), indent=2))


if __name__ == "__main__":
    main()
