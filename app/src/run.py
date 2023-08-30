import yaml
import argparse
import os
from pathlib import Path
from converter_utils import DicomToNiiConverter, NiiToDicomConverter
from registration_utils import registration
from bamf_nnunet_inference import BAMFnnUNetInference
from lung_processor import LungPostProcessor
from total_seg_utils import infer_total_segmentator, get_path
from io_utils import DotDict
import shutil


def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config


def _registration(pt_path, ct_path):
    rct = str(Path(ct_path).parent / str("r" + Path(ct_path).stem + ".gz"))
    if not os.path.isfile(rct):
        registration(pt_path, ct_path)
    return rct
    

def run_nnunet(source_ct_dir, source_pt_dir, target_dir, output_seg_name, num_folds=5, organ_label=9):
    """
    Convert list of dcm files to a single nii.gz file
    :param: source_ct_dir - dir containing list of dcm files
    :param: source_pt_dir - dir containing list of dcm files    
    :param: target_dir - dir to write segmented dcm masks too
    :param: num_folds - number of folds the nnUNet model was trained for
    :param: organ_label - label of lung segment in AIMI dataset    
    """    
    temp_nii_dir = "/tmp/nii-input"
    Path(temp_nii_dir).mkdir(parents=True, exist_ok=True)
    temp_ct_path = os.path.join(temp_nii_dir, "ct_0000.nii.gz")
    temp_pt_path = os.path.join(temp_nii_dir, "ct_0001.nii.gz")

    temp_folds_dir = "/tmp/folds"
    Path(temp_folds_dir).mkdir(parents=True, exist_ok=True)

    # Prepare config for nnUNet model
    WEIGHTS_FOLDER = os.environ["WEIGHTS_FOLDER"]
    TASK_NAME = os.environ["TASK_NAME"]
    model_path = os.path.join(WEIGHTS_FOLDER, f"3d_fullres/{TASK_NAME}/nnUNetTrainerV2__nnUNetPlansv2.1")
    nnunet_inference_model = BAMFnnUNetInference()

    # convert dcm to nii
    converter = DicomToNiiConverter()
    converter.dcm_to_nii(source_ct_dir, temp_ct_path)
    converter.dcm_to_nii(source_pt_dir, temp_pt_path)
    temp_ct_path = _registration(temp_pt_path, temp_ct_path)

    # Infer using nnUNet model across all folds
    organ_name_prefix = "ct_fold"
    for fold_idx in range(num_folds):
        context = {
            'checkpoint_path': model_path,
            'input_file': temp_ct_path,
            'pt_file': temp_pt_path,
            'prediction_save': temp_folds_dir,
            'predict_aug': False,
            'softmax': False,
            'organ_name': f'{organ_name_prefix}_{fold_idx}',
            'fold': fold_idx,
        }
        context = DotDict(context)

        print(f"inferring for fold {fold_idx}")
        print(context)
        output_file = f"{context.organ_name}.nii.gz"
        output_file_path = os.path.join(temp_folds_dir, output_file)
        if not os.path.isfile(output_file_path):
            nnunet_inference_model.handle(context=context)
    
    # Infer using total-segmentator
    total_seg_out_path = infer_total_segmentator(temp_nii_dir, temp_ct_path)

    # ensemble and post process
    lung_post_processor = LungPostProcessor()
    out_file_path = get_path(temp_folds_dir, output_seg_name)
    lung_post_processor.postprocessing(
        save_path=temp_folds_dir,
        ct_path=temp_ct_path,
        total_seg_path=total_seg_out_path,
        out_file_path=out_file_path,
        organ_name_prefix=organ_name_prefix,
        lung_label=organ_label
        )

    # convert nii output back to dcm
    dcmqi_package_path = os.environ["DCMQI_PACKAGE_PATH"]
    converter = NiiToDicomConverter(dcmqi_package_path)
    output_seg_name_dcm = output_seg_name.split('.')[0].strip() + ".dcm"
    target_segmented_dcm_file = get_path(target_dir, output_seg_name_dcm)
    success = converter.convert_nii_to_dcm(
        nii_path=Path(out_file_path),
        dcm_ref_dir=Path(source_ct_dir),
        dcm_out_file=Path(target_segmented_dcm_file),
        dicom_seg_meta_json=Path("dicom_seg_meta.json"),
        add_background_label=False
    )

    # Safety check: If dicom conversion fails, ship the nii file
    if not success:
        target_segmented_nii_file = get_path(target_dir, output_seg_name)
        shutil.copyfile(out_file_path, target_segmented_nii_file)
    print("Execution complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and display YAML configuration")
    parser.add_argument("--config", required=True, help="Path to the YAML configuration file")
    args = parser.parse_args()
    config_path = args.config
    config = load_config(config_path)

    # Load arguments from config
    general = config.get("general", {})
    data_base_dir = general.get("data_base_dir")
    modules = config.get("modules", {})
    nnunet_runner = modules.get("NNUnetRunner", {})
    source_ct_dir = nnunet_runner.get("source_ct_dir")
    source_ct_dir = os.path.join(data_base_dir, source_ct_dir)
    source_pt_dir = nnunet_runner.get("source_pt_dir")
    source_pt_dir = os.path.join(data_base_dir, source_pt_dir)
    target_dir = nnunet_runner.get("target_dir")
    target_dir = os.path.join(data_base_dir, target_dir)    
    num_folds = int(nnunet_runner.get("num_folds"))
    organ_label = int(nnunet_runner.get("organ_label"))
    output_seg_name = nnunet_runner.get("output_seg_name")

    # Run the model
    run_nnunet(
        source_ct_dir=source_ct_dir,
        source_pt_dir=source_pt_dir,
        target_dir=target_dir,
        output_seg_name=output_seg_name,
        num_folds=5,
        organ_label=organ_label
        )
