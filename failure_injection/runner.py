import argparse
import sys
from failure_injection.scenarios import SCENARIOS, set_active_scenario, get_active_scenario

def main():
    parser = argparse.ArgumentParser(description="DataOps Agent Failure Injection Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario", "-s", type=str, choices=list(SCENARIOS.keys()), help="Scenario to activate")
    group.add_argument("--reset", "-r", action="store_true", help="Reset all active failure scenarios")
    group.add_argument("--list", "-l", action="store_true", help="List available failure scenarios")
    group.add_argument("--status", action="store_true", help="Check current active failure scenario")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Failure Injection Scenarios:")
        for name, info in SCENARIOS.items():
            print(f"  - {name}: {info['description']}")
            print(f"    Expected Failure: {info['expected_failure']}\n")
        return

    if args.status:
        active = get_active_scenario()
        if active:
            print(f"Active Scenario: {active}")
        else:
            print("Current State: HEALTHY (No active failure scenario)")
        return

    if args.reset:
        set_active_scenario(None)
        print("Success: Reset failure injection framework. System state restored to HEALTHY.")
        return

    if args.scenario:
        set_active_scenario(args.scenario)
        print(f"Success: Activated failure scenario '{args.scenario}'.")
        print(f"Description: {SCENARIOS[args.scenario]['description']}")
        print(f"Expected Failure: {SCENARIOS[args.scenario]['expected_failure']}")

if __name__ == "__main__":
    main()
