import csv
import os
from faker import Faker


def generate_data(output_path, num_records=10):
    """
    Generate synthetic profile data to be used n the tutorial.

    You can easily generate any other set of fields, please refer to the Faker documentation.
    """
    fake = Faker()
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'current_location', 
            'website', 
            'name', 
            'username', 
            'blood_group', 
            'address', 
            'birthdate', 
            'company', 
            'job', 
            'residence', 
            'mail', 
            'ssn', 
            'sex'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(num_records):
            writer.writerow(fake.profile())


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'profile_data.csv')
    generate_data(output_file)
    print(f'Synthetic profile data generated at {output_file}')
