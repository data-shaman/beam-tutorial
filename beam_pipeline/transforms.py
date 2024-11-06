from io import StringIO  # pylint: disable=missing-module-docstring
import csv
import apache_beam as beam


class ProcessData(beam.DoFn):  # pylint: disable=abstract-method # pylint: disable=missing-class-docstring
    def process(self, element):  # pylint: disable=arguments-differ
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
