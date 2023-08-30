## Summary

Resources to create a container that runs nnUNet model inference on AIMI collection out of the box

### Running instructions
* Create an `input_dir_ct` containing list of `dcm` files corresponding to a given series_id for CT modality
* Create an `input_dir_pt` containing list of `dcm` files corresponding to a given series_id for PT modality 
* Create an `output_dir` to store the output from the model. This is a shared directory mounted on container at run-time. Please assign write permissions to this dir for container to be able to write data
* Next, pull the image from dockerhub:
  * `docker pull bamf:/bamf_nnunet_pt_ct_lung:latest`

* Finally, let's run the container:
  * `docker run --gpus all -v {input_dir_ct}:/app/data/input_data/ct:ro -v {input_dir_pt}:/app/data/input_data/pt -v {output_dir}:/app/data/output_data bamf_nnunet_pt_ct_lung:latest`
* Once the job is finished, the output inference mask(s) would be available in the `{output_dir}` folder

