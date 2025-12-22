#!/usr/bin/env python3
"""
Deploy BHIV workflow to Prefect Cloud using standard Prefect CLI
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Main deployment function"""
    print("BHIV Prefect Cloud Deployment")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("bhiv_workflow.py"):
        print("bhiv_workflow.py not found. Please run from backend directory.")
        sys.exit(1)

    # Step 1: Create deployment using standard Prefect
    print("\nCreating Prefect deployment...")

    # Use prefect deploy with GitHub source
    deploy_cmd = """python -m prefect deploy bhiv_workflow.py:bhiv_workflow \\
        --name bhiv-github-deployment \\
        --description "BHIV AI Assistant workflow from GitHub" \\
        --tag production \\
        --tag ai-assistant \\
        --tag bhiv"""

    if run_command(deploy_cmd, "Creating deployment"):
        print("\nDeployment created successfully!")

        # Step 2: Run the deployment
        print("\nRunning deployment...")
        run_cmd = "python -m prefect deployment run bhiv-ai-assistant/bhiv-github-deployment"

        if run_command(run_cmd, "Running deployment"):
            print("\nBHIV workflow deployed and running!")
            print("\nView your runs at: https://app.prefect.cloud/")

            # Step 3: Optional - Set up schedule
            schedule_choice = input("\nWould you like to schedule this deployment? (y/n): ")
            if schedule_choice.lower() == "y":
                schedule = input("Enter cron schedule (e.g., '0 */6 * * *' for every 6 hours): ")
                schedule_cmd = f"python -m prefect deployment set-schedule bhiv-ai-assistant/bhiv-github-deployment --cron '{schedule}'"
                run_command(schedule_cmd, f"Setting schedule: {schedule}")
        else:
            print("Deployment run failed")
    else:
        print("Deployment creation failed")


if __name__ == "__main__":
    main()
