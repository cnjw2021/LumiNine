import csv
from pathlib import Path

# Constants
DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'csv' / 'daily_astrology_data.csv'
OUTPUT_FILE = Path(__file__).resolve().parent.parent / 'data' / 'csv' / 'pattern_switch_dates.csv'

# Helper to compute next star in ascending / descending

def next_star_asc(num: int) -> int:
    return 1 if num == 9 else num + 1

def next_star_desc(num: int) -> int:
    return 9 if num == 1 else num - 1


def detect_pattern(prev: int, curr: int):
    """Return 'SP_ASC' if (prev->curr) is ascending, 'SP_DESC' if descending, else None"""
    if next_star_asc(prev) == curr:
        return 'SP_ASC'
    elif next_star_desc(prev) == curr:
        return 'SP_DESC'
    return None


def main():
    switches = []  # (date, new_pattern)
    with DATA_FILE.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        prev_row = None
        current_pattern = None
        for row in reader:
            star = int(row['star_number'])
            if prev_row is None:
                prev_row = row
                continue
            prev_star = int(prev_row['star_number'])
            transition = detect_pattern(prev_star, star)
            if transition is None:
                # Skip anomalous data
                prev_row = row
                continue
            if current_pattern is None:
                current_pattern = transition
            elif transition != current_pattern:
                # Pattern switch detected – prev_row is the first day of the new pattern
                switches.append({'date': prev_row['date'], 'pattern': transition})
                current_pattern = transition
            prev_row = row
    # Save to CSV
    with OUTPUT_FILE.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['date', 'pattern']
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        for rec in switches:
            writer.writerow(rec)
    print(f'Saved {len(switches)} switches to {OUTPUT_FILE}')


if __name__ == '__main__':
    main() 