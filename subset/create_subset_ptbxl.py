import os
import shutil
import time
import csv


SOURCE_DIR = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\data\PTB-XL\ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3"
OUTPUT_DIR = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\data\ptbxl_afib_normal_subset"

# We use records500 for 500 Hz (matching training data)
RECORDS_FOLDER = "records500"



def load_ptbxl_database(source_dir):
    """Load the ptbxl_database.csv and return list of records with their labels."""
    csv_path = os.path.join(source_dir, "ptbxl_database.csv")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: ptbxl_database.csv not found at {csv_path}")
        return None
    
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    print(f"Loaded {len(records)} records from ptbxl_database.csv")
    return records


def parse_scp_codes(scp_codes_str):
    """Parse the scp_codes column which is a dict-like string.
    Example: "{'NORM': 100.0}" or "{'AFIB': 80.0, 'STACH': 20.0}"
    """
    try:
        codes = eval(scp_codes_str)
        return codes
    except Exception:
        return {}


def main():
    print("=" * 60)
    print("Creating AFib vs Normal Subset from PTB-XL")
    print("=" * 60)
    print(f"Source:  {SOURCE_DIR}")
    print(f"Output:  {OUTPUT_DIR}")
    print(f"Records: {RECORDS_FOLDER} (500 Hz)")
    print()

    # Load database CSV
    records = load_ptbxl_database(SOURCE_DIR)
    if records is None:
        return

    # Print available columns
    print(f"Columns: {list(records[0].keys())}")
    print()

    # Create output directories
    afib_dir = os.path.join(OUTPUT_DIR, "afib")
    normal_dir = os.path.join(OUTPUT_DIR, "normal")
    os.makedirs(afib_dir, exist_ok=True)
    os.makedirs(normal_dir, exist_ok=True)

    start_time = time.time()
    afib_count = 0
    normal_count = 0
    other_count = 0
    copy_errors = 0

    for row in records:
        scp_codes = parse_scp_codes(row.get('scp_codes', '{}'))
        
        has_afib = 'AFIB' in scp_codes
        has_normal = 'NORM' in scp_codes

        # Determine label — keep AFib or Normal, skip mixed or other
        if has_afib and not has_normal:
            dest_dir = afib_dir
            label = "afib"
        elif has_normal and not has_afib:
            dest_dir = normal_dir
            label = "normal"
        else:
            other_count += 1
            continue

        # Get the filename path from the CSV
        # The 'filename_hr' column has the 500Hz path (e.g., "records500/00000/00001_hr")
        # The 'filename_lr' column has the 100Hz path
        filename_hr = row.get('filename_hr', '').strip()
        
        if not filename_hr:
            other_count += 1
            continue

        # Full path to the record
        record_base = os.path.join(SOURCE_DIR, filename_hr)
        record_name = os.path.basename(filename_hr)

        # Copy all associated files (.hea, .dat, .mat)
        record_dir = os.path.dirname(record_base)
        if not os.path.exists(record_dir):
            copy_errors += 1
            continue

        files_copied = False
        for fname in os.listdir(record_dir):
            # Match files that start with the record name
            if fname.startswith(record_name):
                src = os.path.join(record_dir, fname)
                dst = os.path.join(dest_dir, fname)
                try:
                    shutil.copy2(src, dst)
                    files_copied = True
                except Exception as e:
                    copy_errors += 1

        if files_copied:
            if label == "afib":
                afib_count += 1
            else:
                normal_count += 1

        # Progress
        total_copied = afib_count + normal_count
        if total_copied % 500 == 0 and total_copied > 0:
            elapsed = time.time() - start_time
            print(f"  Copied {total_copied:,} records ({afib_count} AFib, {normal_count} Normal) [{elapsed:.0f}s]")

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"Total records in CSV: {len(records):,}")
    print(f"  AFib:      {afib_count:,} -> {afib_dir}")
    print(f"  Normal:    {normal_count:,} -> {normal_dir}")
    print(f"  Discarded: {other_count:,} (other diagnoses or mixed)")
    print(f"  Errors:    {copy_errors}")
    if afib_count + normal_count > 0:
        print(f"  AFib prevalence: {afib_count / (afib_count + normal_count) * 100:.1f}%")
    print(f"Time: {elapsed:.0f} seconds")

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, "subset_summary.txt")
    with open(summary_path, 'w') as f:
        f.write("PTB-XL: AFib vs Normal Sinus Rhythm Subset\n")
        f.write("=" * 45 + "\n")
        f.write(f"Source: {SOURCE_DIR}\n")
        f.write(f"Records folder: {RECORDS_FOLDER} (500 Hz)\n\n")
        f.write(f"Total records in CSV: {len(records)}\n")
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
