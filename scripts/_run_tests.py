import subprocess, sys, os
os.chdir(r"c:\Repos\Theory of Everything")
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "--tb=line", "-q", "--no-header"],
    capture_output=True, text=True, timeout=300
)
with open(r"c:\Repos\Theory of Everything\_test_final.txt", "w") as f:
    f.write("=== STDOUT ===\n")
    f.write(r.stdout)
    f.write("\n=== STDERR ===\n")
    f.write(r.stderr)
    f.write(f"\n=== RETURNCODE: {r.returncode} ===\n")
print("WROTE FILE")
print("Last 5 lines of stdout:")
for line in r.stdout.strip().split("\n")[-5:]:
    print(line)
print(f"RC={r.returncode}")
