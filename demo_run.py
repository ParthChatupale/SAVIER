import json
import os
import subprocess


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def main() -> None:
    if not os.getenv("DATABASE_URL"):
        raise SystemExit(
            "DATABASE_URL is not set. Example: "
            "postgresql://governance_user:password@localhost:5432/governance_db"
        )
    print("Seeding demo data...")
    run(["python3", "demo_seed.py"])

    base_url = os.getenv("DEMO_API_URL", "http://localhost:8000")
    endpoints = [
        f"{base_url}/api/audit-logs",
        f"{base_url}/api/metrics/global",
        f"{base_url}/api/metrics/velocity",
        f"{base_url}/api/reports",
    ]

    print("\nSample API outputs:")
    for url in endpoints:
        print(f"\nGET {url}")
        output = run(["curl", "-s", url])
        try:
            parsed = json.loads(output)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(output)


if __name__ == "__main__":
    main()
