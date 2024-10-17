import csv
import random
from datetime import datetime
import os

def generate_data(start_year, end_year):
    dates = []
    values = []
    current_year = start_year
    while current_year <= end_year:
        dates.append(f"{current_year}-01")  # January of each year
        values.append(round(random.uniform(2.5, 3.75), 2))  # Random float between 2.5 and 3.75
        
        # Mostly increase by 2 years, but occasionally by 1 year
        if random.random() < 0.2:  # 20% chance to increase by 1 year
            current_year += 1
        else:
            current_year += 2
    
    return dates, values

def create_csv(keyword, dates, values):
    random_number = random.randint(1000, 9999)
    filename = f"BS_{keyword.replace(' ', '_')}_{random_number}.csv"
    full_path = os.path.join('dbase', filename)
    
    # Print the content that will be written to the CSV file
    print(f"\nContent to be written to {full_path}:")
    print(f"Date,{keyword}")  # Print header
    for date, value in zip(dates, values):
        print(f"{date},{value}")
    
    # Now create the actual CSV file
    with open(full_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', keyword])  # Write header
        for date, value in zip(dates, values):
            writer.writerow([date, value])
    
    print(f"CSV file '{full_path}' has been created successfully.")
    return keyword, filename  # Return both keyword and filename

def main():
    # Create the 'dbase' folder if it doesn't exist
    os.makedirs('dbase', exist_ok=True)

    # List of keywords to process
    keywords = [
        "Just in Time",
        "Outsourcing",
        "Project Management",
        "Strategic Planning",
        "Balanced Scorecard",
    ]

    # Generate random data
    start_year = 1994
    end_year = datetime.now().year
    dates, values = generate_data(start_year, end_year)

    # Create a list to store keyword-filename pairs
    index_entries = []

    # Create a CSV file for each keyword
    for keyword in keywords:
        keyword, filename = create_csv(keyword, dates, values)
        index_entries.append((keyword, filename))

    # Create BSindex.txt file
    index_path = os.path.join('dbase', 'BSindex.txt')
    with open(index_path, 'w') as index_file:
        index_file.write("Keyword\t\t\t\tFilename\n")  # Write header with tabs
        for keyword, filename in index_entries:
            index_file.write(f"{keyword}\t\t{filename}\n")
    
    print(f"\nBSindex.txt has been created with the following content:")
    with open(index_path, 'r') as index_file:
        print(index_file.read())

if __name__ == "__main__":
    main()
