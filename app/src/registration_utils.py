import numpy as np
import SimpleITK as sitk
from pathlib import Path


def command_iteration(method):
    print(f"{method.GetOptimizerIteration():3} = {method.GetMetricValue():10.5f}")


def registration(fixed_, moving_, output_path=None):
    fixed = sitk.ReadImage(fixed_, sitk.sitkFloat32)
    moving = sitk.ReadImage(moving_, sitk.sitkFloat32)
    numberOfBins = 24
    samplingPercentage = 0.10
    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsMattesMutualInformation(numberOfBins)
    R.SetMetricSamplingPercentage(samplingPercentage, sitk.sitkWallClock)
    R.SetMetricSamplingStrategy(R.RANDOM)
    R.SetOptimizerAsRegularStepGradientDescent(1.0, 0.001, 200)
    R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
    R.SetInterpolator(sitk.sitkLinear)
    R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))

    outTx = R.Execute(fixed, moving)

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(int(np.min(sitk.GetArrayFromImage(moving))))
    resampler.SetTransform(outTx)
    out = resampler.Execute(moving)
    if not output_path:
        output_path = str(Path(moving_).parent / str("r" + Path(moving_).stem + ".gz"))

    print(output_path)
    out.CopyInformation(fixed)
    sitk.WriteImage(out, output_path)
    return output_path


def registration_img_seg(fixed_, moving_, seg_, output_path=None):
    fixed = sitk.ReadImage(fixed_, sitk.sitkFloat32)
    moving = sitk.ReadImage(moving_, sitk.sitkFloat32)
    seg = sitk.ReadImage(seg_, sitk.sitkFloat32)
    numberOfBins = 24
    samplingPercentage = 0.10
    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsMattesMutualInformation(numberOfBins)
    R.SetMetricSamplingPercentage(samplingPercentage, sitk.sitkWallClock)
    R.SetMetricSamplingStrategy(R.RANDOM)
    R.SetOptimizerAsRegularStepGradientDescent(1.0, 0.001, 200)
    R.SetInitialTransform(sitk.TranslationTransform(fixed.GetDimension()))
    R.SetInterpolator(sitk.sitkLinear)
    R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))
    outTx = R.Execute(fixed, moving)

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(int(np.min(sitk.GetArrayFromImage(seg))))
    resampler.SetTransform(outTx)
    out = resampler.Execute(moving)
    if not output_path:
        output_path = str(Path(moving_).parent / str("r" + Path(moving_).stem + ".gz"))

    print(output_path)
    out.CopyInformation(fixed)
    sitk.WriteImage(out, output_path)
    return output_path


def resample(fixed, moving, output_path=None):
    """
    resample(fixed, moving, output_path)

    """
    fixed_vol = sitk.ReadImage(fixed)
    filt = sitk.ResampleImageFilter()
    filt.SetReferenceImage(fixed_vol)
    filt.SetInterpolator(sitk.sitkNearestNeighbor)
    moving_vol = sitk.ReadImage(moving)
    moving_vol = filt.Execute(moving_vol)
    if not output_path:
        output_path = str(Path(moving).parent / str("r" + Path(moving).stem + ".gz"))

    moving_vol.CopyInformation(fixed_vol)
    sitk.WriteImage(moving_vol, output_path)
    return output_path