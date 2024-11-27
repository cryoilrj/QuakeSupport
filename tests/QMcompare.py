"""
Script to validate QuakeSupport's QuakeMigrate test run against benchmark results

Inputs:
    - QuakeSupport's QuakeMigrate test run results
    - QuakeSupport's QuakeMigrate benchmark results
"""

# --- Import modules ---
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from obspy import read
from obspy.core.util.testing import streams_almost_equal

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Verbose output flag (includes comparison status of file pairs if True)
verbose = True

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

# --- Input paths ---
test_inputs = Path("./inputs")  # Test run inputs directory
test_outputs = Path("./outputs")  # Test run outputs directory
benchmarks_inputs = Path("./benchmarks/inputs")  # Benchmark inputs directory
benchmarks_outputs = Path("./benchmarks/outputs")  # Benchmark outputs directory

# --- XML handling functions ---
IGNORE_XML_TAGS = {"ModuleURI", "Created"}  # Tags excluded in XML comparison


def normalize_xml(xml_file):
    """Parse XML file and remove ignored tags."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Iterate through all parent elements
    for parent in root.iter():
        children = list(parent)
        for child in children:
            # Get local tag name without namespace
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag in IGNORE_XML_TAGS:
                parent.remove(child)

    return ET.tostring(root, encoding="utf-8")


def compare_xml(r1, r2):
    """Check if two XML files are identical, ignoring specified tags."""
    xml1 = normalize_xml(r1)
    xml2 = normalize_xml(r2)
    return xml1 == xml2


def compare_response_xml(test_response, benchmarks_response):
    """Check if two instrument response inventory XML files are identical."""
    print("Comparing instrument response inventory...")

    identical = compare_xml(test_response, benchmarks_response)
    status = "Identical" if identical else "Different"
    if verbose:
        print(f"[XML] {benchmarks_response.name}: {status}")

    if identical:
        print("OK: Instrument response inventories are identical\n")
    else:
        print("Error: Instrument response inventories differ\n")

    return identical


# --- mSEED and text handling functions ---
def compare_mseed(f1, f2):
    """Check if two .mseed files are identical."""
    stream1 = read(f1)
    stream2 = read(f2)
    # streams_almost_equal handles minor differences across OS environments
    return streams_almost_equal(stream1, stream2)


def compare_text(file1, file2):
    """Check if two text files are identical."""
    tolerance = 1e-5  # Numerical tolerance

    with open(file1) as f1, open(file2) as f2:
        for line1, line2 in zip(f1, f2):
            tokens1 = line1.strip().split(",")
            tokens2 = line2.strip().split(",")

            if tokens1 != tokens2:
                for tok1, tok2 in zip(tokens1, tokens2):
                    if tok1 == tok2:
                        continue
                    try:
                        num1, num2 = float(tok1), float(tok2)
                        if not math.isclose(num1, num2, abs_tol=tolerance):
                            return False
                    except ValueError:
                        return False  # Tokens are non-numeric and not equal

        # Check for extra lines in either file
        if any(f1) or any(f2):
            return False

    return True


def compare_files(test_dir, benchmarks_dir, label, wildcard, file_type):
    """Recursively check if specific files in two directories are identical."""
    print(f"Comparing {label} files...")

    # Collect files recursively
    test_files = {f.relative_to(test_dir): f for f in test_dir.rglob(wildcard)}
    benchmarks_files = {
        f.relative_to(benchmarks_dir): f for f in benchmarks_dir.rglob(wildcard)
    }

    # Compare file pairs
    all_identical = True
    for rel_path in sorted(test_files.keys() | benchmarks_files.keys()):
        test_file = test_files.get(rel_path)
        benchmarks_file = benchmarks_files.get(rel_path)

        # Check for missing files
        missing_files = []
        if not test_file:
            missing_files.append("tests")
        if not benchmarks_file:
            missing_files.append("benchmarks")

        if missing_files:
            dirs_join = " and ".join(missing_files)
            print(f"[{label}] {rel_path}: file not found in {dirs_join}")
            all_identical = False
            continue

        if file_type == "mseed":
            identical = compare_mseed(test_file, benchmarks_file)
        elif file_type == "text":
            identical = compare_text(test_file, benchmarks_file)
        status = "Identical" if identical else "Different"
        if verbose:
            print(f"[{label}] {rel_path}: {status}")
        if not identical:
            all_identical = False

    if all_identical:
        print(f"OK: All {label} file pairs are identical\n")
    else:
        print(f"Error: {label} file pairs differ\n")

    return all_identical


if __name__ == "__main__":
    # --- Dictionary to store comparison results ---
    comparison_results = {}

    # --- Compare instrument response inventory ---
    test_response = test_inputs / "response.xml"
    benchmarks_response = benchmarks_inputs / "response.xml"
    response_passed = compare_response_xml(test_response, benchmarks_response)
    comparison_results["response"] = response_passed

    # --- List of input mSEED subdirectories to compare ---
    subdirs = ["raw_mSEED", "aligned_mSEED", "mSEED"]

    # --- Compare input mSEED files in each subdirectory ---
    for subdir in subdirs:
        test_subdir = test_inputs / subdir
        benchmarks_subdir = benchmarks_inputs / subdir

        # Check for missing subdirectories
        missing_subdirs = []
        if not test_subdir.exists():
            missing_subdirs.append("tests")
        if not benchmarks_subdir.exists():
            missing_subdirs.append("benchmarks")

        if missing_subdirs:
            subdirs_join = " and ".join(missing_subdirs)
            print(f"{subdir} directory missing in {subdirs_join}")
            comparison_results[subdir] = False
            continue

        mseed_passed = compare_files(
            test_subdir, benchmarks_subdir, subdir, "*.mseed", "mseed"
        )
        comparison_results[subdir] = mseed_passed

    # --- QuakeMigrate outputs runs directory ---
    test_QM_dir = test_outputs / "runs"
    benchmarks_QM_dir = benchmarks_outputs / "runs"

    # --- Check for missing runs directories ---
    missing_dirs = []
    if not test_QM_dir.exists():
        missing_dirs.append("tests")
    if not benchmarks_QM_dir.exists():
        missing_dirs.append("benchmarks")

    if missing_dirs:
        dirs_join = " and ".join(missing_dirs)
        print(f"runs directory missing in {dirs_join}")
        comparison_results["raw_cut_waveforms"] = False
        comparison_results["events"] = False
        comparison_results["picks"] = False

    else:
        # Compare QuakeMigrate output mSEED, events, and picks files
        QM_mseed_passed = compare_files(
            test_QM_dir, benchmarks_QM_dir, "raw_cut_waveforms", "*.m", "mseed"
        )
        QM_events_passed = compare_files(
            test_QM_dir, benchmarks_QM_dir, "events", "*.event", "text"
        )
        QM_picks_passed = compare_files(
            test_QM_dir, benchmarks_QM_dir, "picks", "*.picks", "text"
        )
        comparison_results["raw_cut_waveforms"] = QM_mseed_passed
        comparison_results["events"] = QM_events_passed
        comparison_results["picks"] = QM_picks_passed

    # --- Summarize comparison results ---
    all_passed = all(comparison_results.values())
    if all_passed:
        print("All comparisons passed")
    else:
        print("Some comparisons failed:")
        for content, result in comparison_results.items():
            if not result:
                print(f"- {content}")
