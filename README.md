# Lung PET/CT Segmentation

We used our FDG-PET/CT lesion segmentation model trained on [AutoPET 2023](https://autopet.grand-challenge.org/) dataset to segment lesions for each of the five folds and ensemble the lesion segments. We then used lungs segmentation from [TotalSegmentator](https://github.com/wasserth/TotalSegmentator) to limit the predicted lesions to only those in the pulmonary and pleural area.

The [model_performance](model_performance.ipynb) notebook contains the code to evaluate the model performance on the following IDC collections against a validation evaluated by a radiologist and a non-expert.

- [TCGA-LUAD](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=6881474)
- [Lung PET-CT Dx](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=70224216)
- [RIDER-Lung-PET-CT](https://wiki.cancerimagingarchive.net/display/Public/RIDER+Lung+PET-CT)
- [ACRIN-NSCLC-FDG-PET](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=39879162)
- [TCGA-LUSC](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=16056484)
- [Anti-PD-1-Lung](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=41517500)
- [NSCLC Radiogenomics](https://wiki.cancerimagingarchive.net/display/Public/NSCLC+Radiogenomics)

## Running the model

- Create an `input_dir_ct` containing list of `dcm` files corresponding to a given series_id for CT modality
- Create an `input_dir_pt` containing list of `dcm` files corresponding to a given series_id for PT modality
- Create an `output_dir` to store the output from the model. This is a shared directory mounted on container at run-time. Please assign write permissions to this dir for container to be able to write data
- Next, pull the image from dockerhub:

  - `docker pull bamfhealth/bamf_nnunet_pt_ct_lung:latest`

- Finally, let's run the container:
  - `docker run --gpus all -v {input_dir_ct}:/app/data/input_data/ct:ro -v {input_dir_pt}:/app/data/input_data/pt -v {output_dir}:/app/data/output_data bamfhealth/bamf_nnunet_pt_ct_lung:latest`
- Once the job is finished, the output inference mask(s) would be available in the `{output_dir}` folder

- Expected output from after successful container run is:
  - `{output_dir}/seg_ensemble_primary.dcm` -- if nifti to dcm conversion is a success
  - `{output_dir}/seg_lesions_ensemble.nii.gz` -- if nifti to dcm conversion is a failure

### Build container from pretrained weights

#TODO

### Running inference

By default the container takes an input directory that contains DICOM files of PET/CT scans from the above mentioned IDC collections, and an output directory where DICOM-SEG files will be placed. To run on multiple scans, place DICOM files for each scan in a separate folder within the input directory. The output directory will have a folder for each input scan, with the DICOM-SEG file inside.

example:

#TODO

There is an optional `--nifti` flag that will take nifti files as input and output.

#### Run inference on IDC Collections

This model was run on PET/CT scans from the above mentioned IDC collections. The AI segmentations and corrections by a radioloist for 10% of the dataset are available in the lung-fdg-pet-ct.zip file on the [zenodo record](https://zenodo.org/record/8352041)

You can reproduce the results with the [run_on_idc_data](run_on_idc_data.ipynb) notebook on google colab.

### Training your own weights

Refer to the [training instructions](training.md) for more details. #TODO
