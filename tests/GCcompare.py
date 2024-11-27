"""
Script to validate QuakeSupport's GrowClust test run against benchmark results

Inputs:
    - QuakeSupport's GrowClust test run and benchmark files:
    1. Event list file
    2. Station list file
    3. xcordata input file
    4. Relocated event catalog file
"""

# --- Import modules ---
import math
from pathlib import Path

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths for test run files
evlist_file = Path("./evlist.txt")  # Event list file
stlist_file = Path("./stlist.txt")  # Station list file
xcordata_file = Path("./xcordata.txt")  # xcordata input file
fout_cat_file = Path("./out.growclust_cat")  # Relocated event catalog file

# Verbose output flag (includes detailed differences if True)
verbose = True

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################


def compare_files(f1_path, f2_path, label):
    """Check if two text files are identical."""
    tolerance = 1e-5  # Numerical tolerance
    has_differences = False  # Flag to track differences

    with open(f1_path, "r", encoding="utf-8") as f1, open(
        f2_path, "r", encoding="utf-8"
    ) as f2:
        f1_lines = [line.strip() for line in f1.readlines()]
        f2_lines = [line.strip() for line in f2.readlines()]

    if f1_lines == f2_lines:
        print(f"OK: {label} files are identical\n")
        return True

    print(f"{label} files appear different, checking within tolerance...")

    # Check if files have different line counts
    if len(f1_lines) != len(f2_lines):
        print(f"{label} files have different line counts")
        if verbose:
            print(f"Test run: {len(f1_lines)} lines")
            print(f"Benchmark: {len(f2_lines)} lines\n")
        return False

    # Find line-wise differences
    for i in range(len(f2_lines)):
        if f1_lines[i] != f2_lines[i]:
            # Split lines into tokens
            f1_tokens = f1_lines[i].split()
            f2_tokens = f2_lines[i].split()

            if len(f1_tokens) != len(f2_tokens):
                if verbose:
                    print(f"Different number of entries at line {i + 1}:")
                    print(f"Test run: {f1_lines[i]}")
                    print(f"Benchmark: {f2_lines[i]}")
                has_differences = True
                continue

            for tok1, tok2 in zip(f1_tokens, f2_tokens):
                try:
                    # Compare floating-point numbers with tolerance
                    num1, num2 = float(tok1), float(tok2)
                    if not math.isclose(num1, num2, abs_tol=tolerance):
                        if verbose:
                            print(f"Difference at line {i + 1}:")
                            print(f"Test run: {f1_lines[i]}")
                            print(f"Benchmark: {f2_lines[i]}")
                        has_differences = True
                        break
                except ValueError:
                    # If tokens are not numbers, compare as regular strings
                    if tok1 != tok2:
                        if verbose:
                            print(f"Difference at line {i + 1}:")
                            print(f"Test run: {f1_lines[i]}")
                            print(f"Benchmark: {f2_lines[i]}")
                        has_differences = True
                        break

    # Account for differences from OS, version, or precision
    if not has_differences:
        print(f"OK: {label} files differ but within tolerance\n")
    else:
        print(f"Error: {label} files differ\n")
    return not has_differences


if __name__ == "__main__":
    # --- Dictionary to store comparison results ---
    comparison_results = {}

    # --- Test run and benchmark files ---
    test_runs = [evlist_file, stlist_file, xcordata_file, fout_cat_file]
    benchmarks = [
        Path("./benchmarks/GrowClust/evlist.txt"),
        Path("./benchmarks/GrowClust/stlist.txt"),
        Path("./benchmarks/GrowClust/xcordata.txt"),
        Path("./benchmarks/GrowClust/out.growclust_cat"),
    ]

    # --- List of text files to compare ---
    file_labels = ["Event list", "Station list", "xcordata", "Relocated event catalog"]

    # --- Compare files ---
    for i, label in enumerate(file_labels):
        test_run_file = test_runs[i]
        benchmark_file = benchmarks[i]
        print(f"Comparing {label} files...")
        file_passed = compare_files(test_run_file, benchmark_file, label)
        comparison_results[label] = file_passed

    # --- Summarize comparison results ---
    all_passed = all(comparison_results.values())
    if all_passed:
        print("All comparisons passed")
    else:
        print("Some comparisons failed:")
        for content, result in comparison_results.items():
            if not result:
                print(f"- {content}")
