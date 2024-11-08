import ants
import numpy as np

dim_mri = mri.shape
dim_ct = ct.shape

# Check if the MRI is smaller than the CT
if dim_mri != dim_ct:
    # Calculate scaling factors for each dimension
    scale_x = dim_ct[0] / dim_mri[0]
    scale_y = dim_ct[1] / dim_mri[1]
    scale_z = dim_ct[2] / dim_mri[2] if len(dim_mri) > 2 else 1  # Check if 3D

    # Create a scaling matrix
    scaling_matrix = np.array([[scale_x, 0, 0, 0],
                                [0, scale_y, 0, 0],
                                [0, 0, scale_z, 0],
                                [0, 0, 0, 1]])

    # Get the affine transformation matrix of the MRI
    affine_mri = mri.affine

    # Scale the affine matrix of the MRI
    scaled_affine_mri = np.dot(affine_mri, scaling_matrix)

    # Resample the MRI image to match the CT size
    resampled_mri = ants.resample_image(mri, ct.shape, use_voxels=True, interp_type='linear')

    # Optionally, apply the new affine transformation to the resampled MRI
    transformed_mri = ants.apply_transforms(fixed=ct, moving=resampled_mri, transformlist=[scaled_affine_mri])

    # Save or display the transformed MRI image
    ants.image_write(transformed_mri, 'path_to_transformed_mri.nii.gz')
else:
    # If they are the same size, you can directly overlay them
    transformed_mri = mri

# Now, you can use ITK-SNAP to overlay `transformed_mri` onto `ct`
