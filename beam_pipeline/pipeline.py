import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from beam_pipeline.transforms import ProcessData


class BeamPipeline:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.pipeline_options = PipelineOptions()

   
    def run(self):
        with beam.Pipeline(options=self.pipeline_options) as p:
            (p  # pylint: disable=expression-not-assigned
             | 'ReadCSV' >> beam.io.ReadFromText(self.input_path, skip_header_lines=1)
             | 'ProcessData' >> beam.ParDo(ProcessData())
             | 'WriteOutput' >> beam.io.WriteToText(self.output_path)
            )
