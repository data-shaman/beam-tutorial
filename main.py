import os
from beam_pipeline.pipeline import BeamPipeline


def main():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    input_file = os.path.join(data_dir, 'profile_data.csv')
    output_file = os.path.join(data_dir, 'output', 'processed_data')

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    pipeline = BeamPipeline(input_file, output_file)
    pipeline.run()


if __name__ == "__main__":
    main()
