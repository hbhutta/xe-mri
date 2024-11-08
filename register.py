try:
    from utils import read_ANTS, get_subdirs
except ImportError as e:
    print(f"An error occurred: {e}")

# from NII import NII
# from multiprocessing.dummy import Pool as ThreadPool
import os
import ants
# from ants.core.ants_image import ANTsImage # may be needed for setting types
from sys import argv
import pickle
from time import time
start_time = time()
NUM_THREADS = os.cpu_count()
# print(f'Number of threads: {NUM_THREADS}')  # 64
BASE_DIR = argv[1]
subdir_paths = get_subdirs(dir=BASE_DIR)
# print(subdir_paths)


def register(ct_filename: str, mri_filename: str, patient: str) -> None:
    # tried: Similarity, Affine, also try AffineFast
    ct_ants = ants.image_read(filename=ct_filename)
    mri_ants = ants.image_read(filename=mri_filename)

    type_of_transform = "Similarity"
    prep = ants.registration(
        fixed=ct_ants, moving=mri_ants, type_of_transform=type_of_transform, verbose=True)

    transform_file = prep['fwdtransforms'][0]
    print('Using initial transformation file: {}'.format(transform_file))

    reg = ants.registration(fixed=ct_ants,
                            moving=mri_ants,
                            type_of_transform='SyNAggro',  # deformation
                            initial_transform=transform_file,
                            outprefix='',
                            mask=None,
                            moving_mask=None,
                            grad_step=0.2,
                            flow_sigma=3,
                            total_sigma=0,
                            aff_metric="mattes",
                            aff_sampling=16,
                            aff_random_sampling_rate=0.2,
                            syn_metric="mattes",
                            syn_sampling=16,
                            reg_iterations=(40, 20, 0),
                            aff_iterations=(2100, 1200, 1200, 10),
                            aff_shrink_factors=(6, 4, 2, 1),
                            aff_smoothing_sigmas=(3, 2, 1, 0),
                            write_composite_transform=False,
                            random_seed=1,  # set to 1 for reproducibility
                            verbose=True,
                            multivariate_extras=None)

    print(f"Finished similarity registration for patient {
          os.path.basename(patient)}!\n\n\n")

    with open(f"{patient}/{os.path.basename(patient)}_reg.pkl", "wb") as file:
        pickle.dump(reg, file)
        print(f"{patient}/{os.path.basename(patient)}_reg.pkl saved!")


ct_nii = read_ANTS(as_type='ct', dir=BASE_DIR, ret_ants=False,
                   ct_filename="CT_mask_neg_affine.nii")
mri_nii = read_ANTS(as_type='proton', dir=BASE_DIR, ret_ants=False,
                    mr_filename="mask_reg_edited_scaled_mutated_affine.nii")
vent_nii = read_ANTS(as_type='vent', dir=BASE_DIR,
                     ret_ants=False, vent_filename="gas_highreso_scaled_mutated_affine.nii")

# print(ct_nii, mri_nii, vent_nii, subdir_paths)
# assert 0 == 1
for ct, mri, vent, patient in zip(ct_nii, mri_nii, vent_nii, subdir_paths):
    print(f"ct {ct} | mri {mri} | vent {
          vent} | patient {os.path.basename(patient)}")
    register(ct_filename=ct, mri_filename=mri, patient=patient)
end_time = time()
print(f"That took: {end_time - start_time} mins/seconds")
