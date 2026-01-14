#!/usr/bin/env python3
"""Quick deployment script for Render"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[✓] {description} - Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[✗] {description} - Failed")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print("=" * 80)
    print("Render Deployment Script")
    print("=" * 80)

    # Check if git is initialized
    print("\n[*] Checking git status...")
    result = subprocess.run("git status", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("[!] Git not initialized. Initializing...")
        run_command("git init", "Initialize git repository")

    # Add all files
    if not run_command("git add .", "Add all files to git"):
        sys.exit(1)

    # Commit changes
    commit_msg = input("\nEnter commit message (or press Enter for default): ").strip()
    if not commit_msg:
        commit_msg = "Prepare for Render deployment"

    if not run_command(f'git commit -m "{commit_msg}"', "Commit changes"):
        print("[!] Nothing to commit or commit failed")

    # Check if remote exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        print("\n[!] No git remote found.")
        remote_url = input("Enter your GitHub repository URL: ").strip()
        if remote_url:
            run_command(f"git remote add origin {remote_url}", "Add git remote")

    # Push to GitHub
    print("\n[*] Ready to push to GitHub")
    push = input("Push to GitHub now? (y/n): ").strip().lower()
    if push == 'y':
        if not run_command("git push -u origin main", "Push to GitHub"):
            print("[!] Push failed. You may need to:")
            print("    1. Create the repository on GitHub first")
            print("    2. Set up authentication (SSH key or Personal Access Token)")
            print("    3. Try: git push -u origin main --force (if needed)")

    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("\n1. Go to https://dashboard.render.com")
    print("2. Click 'New +' → 'Web Service'")
    print("3. Connect your GitHub repository")
    print("4. Render will auto-detect render.yaml configuration")
    print("5. Add environment variables (see RENDER_DEPLOYMENT_GUIDE.md)")
    print("6. Click 'Create Web Service'")
    print("\n✅ Your code is ready for Render deployment!")
    print("=" * 80)

if __name__ == "__main__":
    main()
