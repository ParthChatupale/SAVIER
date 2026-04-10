import argparse
import json
import redis


def main() -> None:
    parser = argparse.ArgumentParser(description="Print recent telemetry events from Redis.")
    parser.add_argument("-n", "--count", type=int, default=10, help="Number of events to print")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--db", type=int, default=0, help="Redis database index")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON strings")
    parser.add_argument(
        "--list",
        default="incoming_logs_history",
        help="Redis list name (default: incoming_logs_history)",
    )
    args = parser.parse_args()

    client = redis.Redis(host=args.host, port=args.port, db=args.db, decode_responses=True)
    count = max(args.count, 1)
    list_name = args.list
    items = client.lrange(list_name, 0, count - 1)

    if not items and list_name == "incoming_logs_history":
        # Fall back to the live queue if history is empty.
        list_name = "incoming_logs"
        items = client.lrange(list_name, 0, count - 1)

    if not items:
        print(f"No events in {list_name}.")
        return

    for idx, item in enumerate(items, start=1):
        print(f"\n--- event {idx} ({list_name}) ---")
        if args.raw:
            print(item)
            continue
        try:
            parsed = json.loads(item)
            print(json.dumps(parsed, indent=2, sort_keys=True))
        except json.JSONDecodeError:
            print(item)


if __name__ == "__main__":
    main()
