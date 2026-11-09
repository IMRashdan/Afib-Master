import os
import shutil
import time


SOURCE_DIR = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\data\Georgia"
OUTPUT_DIR = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\data\georgia_afib_normal_subset"

AFIB_CODE = "164889003"       # Atrial Fibrillation
NORMAL_CODE = "426783006"     # Normal Sinus Rhythm



def parse_diagnosis_from_hea(hea_path):
    """Read the #Dx line from a .hea file and return list of SNOMED codes."""
    codes = []
    with open(hea_path, 'r') as f:
        for line in f:
            if line.startswith('#Dx:'):
                code_str = line.strip().split(':')[1].strip()
                codes = [c.strip() for c in code_str.split(',')]
                break
    return codes


def main():
    assert os.path.exists(SOURCE_DIR), f"Source folder not found: {SOURCE_DIR}"

    # Create output directories
    afib_dir = os.path.join(OUTPUT_DIR, "afib")
    normal_dir = os.path.join(OUTPUT_DIR, "normal")
    os.makedirs(afib_dir, exist_ok=True)
    os.makedirs(normal_dir, exist_ok=True)

    print("=" * 60)
    print("Creating AFib vs Normal Subset from Georgia Database")
    print("=" * 60)
    print(f"Source:  {SOURCE_DIR}")
    print(f"Output:  {OUTPUT_DIR}")
    print(f"AFib code:   {AFIB_CODE}")
    print(f"Normal code: {NORMAL_CODE}")
    print()

    start_time = time.time()
    total_records = 0
    afib_count = 0
    normal_count = 0
    other_count = 0

    # Walk through all subfolders to find .hea files
    for root, dirs, files in os.walk(SOURCE_DIR):
        hea_files = [f for f in files if f.endswith('.hea')]
        for hea_file in hea_files:
            total_records += 1
            hea_path = os.path.join(root, hea_file)
            record_name = os.path.splitext(hea_file)[0]

            codes = parse_diagnosis_from_hea(hea_path)
            has_afib = AFIB_CODE in codes
            has_normal = NORMAL_CODE in codes

            # Keep AFib (even with other conditions) or Normal (even with other conditions)
            # Skip if record has BOTH AFib and Normal, or neither
            if has_afib and not has_normal:
                dest_dir = afib_dir
                afib_count += 1
            elif has_normal and not has_afib:
                dest_dir = normal_dir
                normal_count += 1
            else:
                other_count += 1
                continue

            # Copy all files for this record (.hea, .mat, .dat)
            for fname in os.listdir(root):
                if fname.startswith(record_name + ".") or fname.startswith(record_name + "_"):
                    src = os.path.join(root, fname)
                    dst = os.path.join(dest_dir, fname)
                    shutil.copy2(src, dst)

            # Progress
            copied = afib_count + normal_count
            if copied % 500 == 0 and copied > 0:
                elapsed = time.time() - start_time
                print(f"  Copied {copied:,} records ({afib_count} AFib, {normal_count} Normal) [{elapsed:.0f}s]")

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"Total records scanned: {total_records:,}")
    print(f"  AFib:      {afib_count:,} -> {afib_dir}")
    print(f"  Normal:    {normal_count:,} -> {normal_dir}")
    print(f"  Discarded: {other_count:,} (other diagnoses)")
    if afib_count + normal_count > 0:
        print(f"  AFib prevalence: {afib_count / (afib_count + normal_count) * 100:.1f}%")
    print(f"Time: {elapsed:.0f} seconds")

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, "subset_summary.txt")
    with open(summary_path, 'w') as f:
        f.write("Georgia 12-Lead ECG: AFib vs Normal Sinus Rhythm Subset\n")
        f.write("=" * 55 + "\n")
        f.write(f"Source: {SOURCE_DIR}\n")
        f.write(f"AFib SNOMED code: {AFIB_CODE}\n")
        f.write(f"Normal SNOMED code: {NORMAL_CODE}\n\n")
        f.write(f"Total records scanned: {total_records}\n")
        f.write(f"AFib records:   {afib_count}\n")
        f.write(f"Normal records: {normal_count}\n")
        f.write(f"Discarded:      {other_count}\n")
        if afib_count + normal_count > 0:
            f.write(f"AFib prevalence: {afib_count / (afib_count + normal_count) * 100:.1f}%\n")

        f.write(f"\nAFib records ({afib_count}):\n")
        for fname in sorted(os.listdir(afib_dir)):
            if fname.endswith('.hea'):
                f.write(f"  {os.path.splitext(fname)[0]}\n")

        f.write(f"\nNormal records ({normal_count}):\n")
        for fname in sorted(os.listdir(normal_dir)):
            if fname.endswith('.hea'):
                f.write(f"  {os.path.splitext(fname)[0]}\n")

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
