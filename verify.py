"""
Quick verification script for DevSecOps Pipeline
Run this before your presentation to ensure everything works
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print()

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print(f"✓ {description} - PASSED")
            return True
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"✗ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {str(e)}")
        return False


def main():
    """Run all verification tests"""
    print("="*60)
    print("DevSecOps Pipeline Verification")
    print("="*60)

    results = []

    # Test 1: Check Python version
    results.append(run_command(
        "python --version",
        "Python version check"
    ))

    # Test 2: Check Docker
    results.append(run_command(
        "docker --version",
        "Docker installation check"
    ))

    # Test 3: Check Docker Compose
    results.append(run_command(
        "docker-compose --version",
        "Docker Compose installation check"
    ))

    # Test 4: Check project structure
    results.append(run_command(
        "dir /B app\\src\\*.py",
        "Project structure check"
    ))

    # Test 5: Check security tools
    results.append(run_command(
        "bandit --version",
        "Bandit installation check"
    ))

    results.append(run_command(
        "safety --version",
        "Safety installation check"
    ))

    # Test 7: Check code quality tools
    results.append(run_command(
        "black --version",
        "Black installation check"
    ))

    results.append(run_command(
        "flake8 --version",
        "Flake8 installation check"
    ))

    # Test 8: Check test framework
    results.append(run_command(
        "pytest --version",
        "Pytest installation check"
    ))

    # Test 9: Build Docker image
    print("\n" + "="*60)
    print("Testing: Docker image build")
    print("="*60)
    print("This may take a few minutes...")
    try:
        result = subprocess.run(
            "docker build -t devsecops-app:verify app/",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        if result.returncode == 0:
            print("✓ Docker image build - PASSED")
            results.append(True)
        else:
            print("✗ Docker image build - FAILED")
            print(result.stderr)
            results.append(False)
    except Exception as e:
        print(f"✗ Docker image build - ERROR: {str(e)}")
        results.append(False)

    # Test 10: Run unit tests
    print("\n" + "="*60)
    print("Testing: Unit tests")
    print("="*60)
    try:
        result = subprocess.run(
            "pytest app/tests/ -v --tb=short",
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✓ Unit tests - PASSED")
            results.append(True)
        else:
            print("✗ Unit tests - FAILED")
            results.append(False)
    except Exception as e:
        print(f"✗ Unit tests - ERROR: {str(e)}")
        results.append(False)

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n✓ All checks passed! You're ready for your presentation.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
