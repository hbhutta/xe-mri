import os
import ants
import pickle
from time import time


def register(ct_filename: str, mri_filename: str, dir: str) -> None:
    patient_PIm_ID = os.path.basename(dir[:-1])
    print(patient_PIm_ID)
    reg_filename = f"{dir}{patient_PIm_ID}_reg.pkl"
    print(reg_filename) 
    print(os.path.exists(reg_filename))
    return
    if not os.path.exists(reg_filename):
        print(f"Creating {reg_filename} ...") # e.g. imgs/PIm0216/PIm0216_reg.pkl
        print(f"Performing CT-MRI registration...")
        start_time = time()
        print(type(ct_filename))
        ct_ants = ants.image_read(filename=ct_filename)

        print(mri_filename)
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

        print(f"Finished similarity registration for patient {patient_PIm_ID}!\n\n\n")

        with open(reg_filename, "wb") as file:
            pickle.dump(reg, file)
            print(f"Registration output serialized to {reg_filename}")
        end_time = time()
        print(f"That took: {end_time - start_time} mins/seconds")

    else:
        print(f"The registration output {reg_filename} already exists")
