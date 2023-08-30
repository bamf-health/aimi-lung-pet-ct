import os 


def get_path(*paths):
    """
    Concatenate paths to create a complete file path.

    Args:
        *paths: Variable number of path segments.

    Returns:
        str: Complete file path.
    """
    return os.path.join(*paths)


def infer_total_segmentator(save_path, ct_path):
    """
    Perform inference using TotalSegmentator on the provided CT image.

    Args:
        save_path (str): Path to save the segmentation result.
        ct_path (str): Path to the CT image for segmentation.
    """
    output_path = get_path(save_path, 'totalsegmentator.nii.gz')
    if not os.path.isfile(output_path):
        os.system(f"TotalSegmentator -i {ct_path} -o {output_path} --ml")
    return output_path