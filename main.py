from logger import logger
import os
from time import sleep
from absl import app, flags

from classes.Image import NII
from utils.os_utils import contains_subdir, get_files, get_subdirs, list2str
from utils.nifti_utils import mod_field, disp_field
from utils.enums import CODE
import nibabel as nib
from nibabel.nifti1 import Nifti1Image
from nibabel.orientations import aff2axcodes

import subprocess


def get_axcodes(img: Nifti1Image) -> tuple:
    return aff2axcodes(aff=img.affine, labels=(('L', 'R'), ('P', 'A'), ('I', 'S')))

# from scripts.reorient import reorient
# from scripts.register import register
# from scripts.unpack import unpack
# from scripts.unzip import unzip
# from scripts.warp_vent import warp_vent


FLAGS = flags.FLAGS
flags.DEFINE_string(name="dir", default=None, help="""
                    Pass in a directory to this flag.

                    If this directory is a directory of patients
                    where each patient is its own directory, then
                    the entire program will run for each patient.

                    If the directory passed is for a single patient,
                    only that patient's files will be processed.

                    This is for convenience and testing purposes.

                    In some use cases, you may want to run the pipeline
                    just for a single patient.
                    """, required=True)


def process(patient_dir: str) -> None:
    ct_img = NII(filename=get_files(dir=patient_dir, files="CT.nii"))
    ct_mask = NII(filename=get_files(dir=patient_dir, files="CT_mask.nii"))

    for img in [ct_img, ct_mask]:
        logger.info(f"Checking sform codes for {img.get_filename()}")
        out = None

        # Ensure that sform_code = 1
        if img.get_sform_code() == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh",
                                  "-f", "sform_code",                   # Field to modify
                                  "-v", "1",                            # New value
                                  # NIFTI file
                                  "-n", f"{img.get_filename()}"])
            logger.info(out.stdout)
        else:
            logger.info(f"sform_code is already 1")
        sleep(2)

        # Ensure that quatern_d = 1
        if img.get_quatern("d") == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh",
                                  "-f", "quatern_d",                    # Field to modify
                                  "-v", "1",                            # New value
                                  # NIFTI file
                                  "-n", f"{img.get_filename()}"])
            logger.info(out.stdout)
            logger.info(f"The unit quaternion is now: {
                        img.get_unit_quaternion()}")
        else:
            logger.info(f"quatern_d is already 1")
        sleep(2)

        # Ensure that qform_code = 1
        if img.get_qform_code() == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh",
                                  "-f", "qform_code",                   # Field to modify
                                  "-v", "1",                            # New value
                                  # NIFTI file
                                  "-n", f"{img.get_filename()}"])
            logger.info(out.stdout)
        else:
            logger.info(f"qform_code is already 1")
        sleep(2)

        logger.info(f"Original sform affine:\n{img.get_sform()}")
        logger.info(f"Original qform affine:\n{img.get_qform()}")

        # Reload image because original data was changed by script
        img = NII(filename=get_files(dir=patient_dir,
                  files=os.path.basename(img.get_filename())))
        img.save(filename=img.get_filename())

        logger.info(f"New sform affine:\n{img.get_sform()}")
        logger.info(f"New qform affine:\n{img.get_qform()}")
        continue

        if out != None and out.returncode == 0:
            logger.info(f"{img.get_filename()} has sform code changed")
            logger.info(f"New sform_code of {img.get_filename()}: {
                        img.get_sform_code()}")

        ax = ''.join(img.get_axcodes())
        logger.info(f"File {img.get_filename()
                            } currently has RAS orientation: {ax}")

        if ax != "RAS":
            img.toRAS()
            print(img.get_sform())
            # assert img.get_axcodes() == tuple("RAS")
            logger.info(f"File {img.get_filename()} has axcodes {
                        img.get_axcodes()} after reorientation.")
        else:
            logger.info(
                f"File {img.get_filename()} in proper orientation (RAS). Leaving unchanged...")

    assert 0 == 1
    logger.info(
        f"xform codes and orientation fixed, aligning CT image to mask...")
    x, y, z = ct_img.get_origin()
    ct_mask.translate(x, y, z)

    try:
        assert ct_mask.is_matched_by_origin(ct_img)
        ct_mask.save(ct_mask.get_filename()[:-4] + "_translated.nii")
        logger.info(f"Image {ct_mask.get_filename()} saved!")
    except AssertionError as e:
        logger.info(f"Unable to match origin of {
                    ct_mask.get_filename()} to origin of {ct_img.get_filename()}!")
        return

    # for fn in original_files[1:]:  # Resize all files except for CT_mask.nii
    #     print(patient_dir)
    #     print(os.path.basename(fn))
    #     resize(img_path=fn)

    post_resize_files = get_files(dir=patient_dir, files=[
        "CT.nii",
        "CT_mask.nii",
        "mask_reg_edited_scaled.nii",
        "gas_highreso_scaled.nii",
        "rbc2gas_scaled.nii",
        "membrane2gas_scaled.nii"
    ])

#    for fn in post_resize_files:
#        if "CT_mask" in fn:
#            reorient(file=fn, key=ReorientKey.CT.value)
#        else:
#            reorient(file=fn, key=ReorientKey.VENT.value)
#
#    files = [  # After resizing and reorienting
#        "CT_nii",
#        "CT_mask_neg_affine.nii",
#        "mask_reg_edited_scaled_mutated_affine.nii",
#        "gas_highreso_scaled_mutated_affine.nii",
#        "rbc2gas_scaled_mutated_affine.nii",
#        "membrane2gas_scaled_mutated_affine.nii"
#    ]
#
#    ct_file, mr_file, gas, rbc, mem = [
#        os.path.join(patient_dir, fn) for fn in files]
#
#    # Assert files exist *after* reorienting and resizing
#    for fn_path in [os.path.join(patient_dir, fn) for fn in files]:
#        if not os.path.exists(fn_path):
#            raise Exception(f"""
#                  File {fn_path} does not exist for patient {patient_dir[5:]}
#                  but it is required for processing them in this pipeline.
#                  """)
#
#    print(f"ct {ct_file} | mr {mr_file} | gas {gas} | rbc {rbc} | mem {mem}")
#
#    register(ct_filename=ct_file, mri_filename=mr_file, dir=patient_dir)
#    unpack(ct_file=ct_file, dir=patient_dir)
#    unzip(os.path.join(patient_dir, "warped_mri.nii.gz"))
#
#    for ven in [gas, rbc, mem]:
#        warp_vent(ct=ct_file, dir=patient_dir, vent=ven)
#
#


"""
If qfac = 1 -> RAI is proper
if qfac = -1 -> RAS is proper
"""


def main(argv):
    dir_ = FLAGS.dir
    print(dir_)
    if contains_subdir(dir_):
        print("Recieved a batch directory of multiple patients.")
        for subdir in get_subdirs(dir_):
            print(f"Processing patient {subdir[5:]}")

            CT = nib.load(get_files(dir=subdir, files="CT.nii"))
            CT_mask = nib.load(get_files(dir=subdir, files="CT_mask.nii"))

            pixdim_1 = float(CT.header['pixdim'][1])
            pixdim_2 = float(CT.header['pixdim'][2])
            pixdim_3 = float(CT.header['pixdim'][3])

            qoffset_x = float(CT.header['qoffset_x'])
            qoffset_y = float(CT.header['qoffset_y'])
            qoffset_z = float(CT.header['qoffset_z'])

            if (CT.header['pixdim'][0]) == 1:
                srow_x = [-1*pixdim_1, 0., 0., qoffset_x]
                srow_y = [0., -1*pixdim_2, 0., qoffset_y]
                srow_z = [0., 0., 1*pixdim_3, qoffset_z]
            elif (CT.header['pixdim'][0]) == -1:
                srow_x = [-1*pixdim_1, 0., 0., qoffset_x]
                srow_y = [0., -1*pixdim_2, 0., qoffset_y]
                srow_z = [0., 0., -1*pixdim_3, qoffset_z]

            mod_field(CT.get_filename(), field="srow_x",
                      value=list2str(srow_x))
            mod_field(CT.get_filename(), field="srow_y",
                      value=list2str(srow_y))
            mod_field(CT.get_filename(), field="srow_z",
                      value=list2str(srow_z))

            CT = nib.load(get_files(dir=subdir, files="CT.nii"))

            if CT_mask.header['pixdim'][0] != CT.header['pixdim'][0]:
                pixdim = CT_mask.header['pixdim']
                # CT.header['pixdim][0] # Make the qfac match that of the CT ???
                pixdim[0] = CT.header['pixdim'][0]
                mod_field(CT_mask.get_filename(),
                          field="pixdim", value=list2str(pixdim))
                CT_mask = nib.load(get_files(dir=subdir, files="CT_mask.nii"))

            if CT.header['qform_code'] != 1:
                mod_field(CT.get_filename(), field="qform_code", value=1)
                CT = nib.load(get_files(dir=subdir, files="CT.nii"))

            if CT.header['sform_code'] != 1:
                mod_field(CT.get_filename(), field="sform_code", value=1)
                CT = nib.load(get_files(dir=subdir, files="CT.nii"))

            if CT.header['quatern_d'] != 1:
                mod_field(CT.get_filename(), field="quatern_d", value=1)
                CT = nib.load(get_files(dir=subdir, files="CT.nii"))

            if CT_mask.header['qform_code'] != 1:
                mod_field(CT_mask.get_filename(), field="qform_code", value=1)
                CT_mask = nib.load(get_files(dir=subdir, files="CT_mask.nii"))

            if CT_mask.header['sform_code'] != 1:
                mod_field(CT_mask.get_filename(), field="sform_code", value=1)
                CT_mask = nib.load(get_files(dir=subdir, files="CT_mask.nii"))

            if CT_mask.header['quatern_d'] != 1:
                mod_field(CT_mask.get_filename(), field="quatern_d", value=1)
                CT_mask = nib.load(get_files(dir=subdir, files="CT_mask.nii"))

            print("CT axcodes: ", get_axcodes(CT))
            print("CT_mask axcodes: ", get_axcodes(CT_mask))
            print("qfac: ", CT.header['pixdim'][0])
            print("srow_x: ", CT.header['srow_x'])
            print("srow_y: ", CT.header['srow_y'])
            print("srow_z: ", CT.header['srow_z'])

            # Translate (encode change in mask qoffsets)
            mask_new_q_offset_x = float(CT.header['qoffset_x'])
            mask_new_q_offset_y = float(CT.header['qoffset_y'])
            mask_new_q_offset_z = float(CT.header['qoffset_z'])

            mod_field(CT_mask.get_filename(), field="qoffset_X",
                      value=list2str(mask_new_q_offset_x))
            mod_field(CT_mask.get_filename(), field="qoffset_y",
                      value=list2str(mask_new_q_offset_y))
            mod_field(CT_mask.get_filename(), field="qoffset_z",
                      value=list2str(mask_new_q_offset_z))

            # Translate (encode change in mask srow_x origin)
            mask_new_pixdim_1 = float(CT.header['pixdim'][1])
            mask_new_pixdim_2 = float(CT.header['pixdim'][2])
            mask_new_pixdim_3 = float(CT.header['pixdim'][3])

            mod_field(CT_mask.get_filename(), field="srow_x",
                      value=list2str(mask_new_pixdim_1))
            mod_field(CT_mask.get_filename(), field="srow_y",
                      value=list2str(mask_new_pixdim_2))
            mod_field(CT_mask.get_filename(), field="srow_z",
                      value=list2str(mask_new_pixdim_3))


#            process(patient_dir=subdir)
    else:
        print("Recieved a directory of single patient.")
        print(f"Processing patient {dir_[5:]}")
#        process(patient_dir=dir_)


if __name__ == "__main__":
    app.run(main)
