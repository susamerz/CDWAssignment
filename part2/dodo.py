"""
Do-it script to execute the entire pipeline using the doit tool:
http://pydoit.org
"""
import config

# Configuration for the "doit" tool.
DOIT_CONFIG = dict(
    # When the user executes "doit list", list the tasks in the order they are
    # defined in this file, instead of alphabetically.
    sort='definition',
)

def task_preprocessing():
    """Step 01: Perform preprocessing of the data."""
    for subject in config.subjects:
        yield dict(
            name=f'subj{subject}',
            file_dep=[
                config.input_data_path / f'subj{subject}' / 'bold.nii.gz',
                config.input_data_path / f'subj{subject}' / 'labels.txt',
                '01_preprocessing.py'
            ],
            targets=[
                config.output_data_path / f'subj{subject}' / 'bold_preprocessed.nii.gz',
                config.output_data_path / f'subj{subject}' / 'labels_preprocessed.txt'
            ],
            actions=[f'python 01_preprocessing.py {subject}'],
        )

def task_rsa():
    """Step 02: Perform RSA."""
    for subject in config.subjects:
        yield dict(
            name=f'subj{subject}',
            file_dep=[
                config.output_data_path / f'subj{subject}' / 'bold_preprocessed.nii.gz',
                config.output_data_path / f'subj{subject}' / 'labels_preprocessed.txt',
                config.input_data_path / f'subj{subject}' / 'mask4_vt.nii.gz',
                '02_rsa.py',
            ],
            targets=[
                config.output_data_path / f'subj{subject}' / 'rsa_result.nii.gz',
                config.output_data_path / f'subj{subject}' / 'rdm_model.npz'
            ],
            actions=[f'python 02_rsa.py {subject}'],
        )

def task_grand_average():
    """Step 03: Create grand average."""
    return dict(
        file_dep=[config.output_data_path / f'subj{subject}' / 'rsa_result.nii.gz'
                  for subject in config.subjects] + ['03_grand_average.py'],
        targets=[config.output_data_path / 'rsa_grand_average.nii.gz'],
        actions=['python 03_grand_average.py'],
    )
