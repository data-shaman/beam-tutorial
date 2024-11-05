from io import StringIO
import apache_beam as beam
import csv


class ProcessData(beam.DoFn):
    def process(self, element):
        reader = csv.DictReader(StringIO(element), fieldnames=[
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
        ])
        for row in reader:
            # Example processing: uppercase the name
            row['name'] = row['name'].upper()
            yield row
