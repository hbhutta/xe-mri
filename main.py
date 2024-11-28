from absl import app, flags

from classes.Image import NII
from utils.utils import *
from utils.enums import CODE

from nibabel.nifti1 import Nifti1Image

# from scripts.reorient import reorient
# from scripts.register import register
# from scripts.unpack import unpack
# from scripts.unzip import unzip
# from scripts.warp_vent import warp_vent

from logger import logger

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
    # Minimum set of files that must exist for any patient, with exactly these names

    original_files = get_files(dir=patient_dir, files=[
        "CT.nii",
        "CT_mask.nii",
        "mask_reg_edited.nii",
        "gas_highreso.nii",
        "rbc2gas.nii",
        "membrane2gas.nii"
    ])

    ct_img = NII(filename=original_files[0])
    ct_mask = NII(filename=original_files[1])
    ct_img_copy = NII(filename=original_files[0])
    img = nib.load("imgs_copy_new/PIm0216/CT.nii")
    flip_ct_or_mri(img, type=True)
    nib.save(img,  "imgs_copy_new/PIm0216/CT_testing123.nii")
    assert 0 == 1
    
    
    hdr = ct_img_copy.get_header()
    hdr['sform_code'] = 1
    hdr['qform_code'] = 1
    ct_img_copy._NII__save_header(hdr)
    ct_img_copy.save("imgs_copy_new/PIm0216/CT_testing123.nii")
    assert 0 == 1
    print(hdr)
#    assert 0 == 1
    affine = hdr.get_qform() 
    dataobj = ct_img.get_fdata()
    nii_img = Nifti1Image(dataobj=dataobj, affine=affine, header=hdr)
    nib.save(nii_img, "imgs_copy_new/PIm0216/CT_testing123.nii")
    assert 0 == 1
    print("original")
    print(ct_img.get_qform())
    print(ct_img.get_sform())
#    print(ct_mask.get_qform())
#    print(ct_mask.get_sform())
    print(ct_img.get_sform_code())
    print(ct_img.get_qform_code())
    ct_img.toRAS()
    print(ct_img.get_qform())
    print(ct_img.get_sform())
    assert 0 == 1
    ct_img.save(ct_img.get_filename()[:-4] + "_dummy.nii") 
    ct_mask.save(ct_mask.get_filename()[:-4] + "_dummy.nii") 

    assert 0 == 1 
    for img in [ct_img, ct_mask]:
        logger.info(f"Detected {str(img.get_axcodes())} axcodes for NIFTI image {img.get_filename()}")

    if (ct_img.get_axcodes() != tuple("RAS") and ct_mask.get_axcodes() != tuple("RAS")):
        for img in [ct_img, ct_mask]:
            if img.get_sform_code() != CODE.SCANNER.value:
                logger.info(f"{img.get_filename()} has sform_code = {img.get_sform_code()}. Setting to 1 (scanner).")
                img.set_sform_code(CODE.ALIGNED)    
                img.set_sform_code(CODE.SCANNER)    
                print(f"new code: {img.get_sform_code()}")           
                
        
                
        ct_img.toRAS()
        ct_mask.toRAS()
        ct_mask.translate(z=ct_img.get_origin()[2])
        
       
        ct_img.save(ct_img.get_filename()[:-4] + "_RAS.nii")
        ct_mask.save(ct_mask.get_filename()[:-4] + "_RAS.nii")
        
        assert 0 == 1
        print(ct_img.get_affine())
        print(ct_mask.get_affine()) 
        
        print(ct_img.get_axcodes())
        print(ct_mask.get_axcodes())

    elif (ct_img.get_axcodes() == tuple("RAS") and ct_mask.get_axcodes() == tuple("RAS")):
        """In the case where both the reference and the mask are in RAS, 
        is sufficient to translate the mask to match the origin of the reference"""
        x, y, z = ct_img.get_origin()
        ct_mask.translate(x, y, z)
        try: 
            #assert ct_mask.is_matched_by_origin(ct_img)
            ct_mask.save(ct_mask.get_filename()[:-4] + "_translated.nii")
            logger.info(f"Image {ct_mask.get_filename()} saved!")
        except AssertionError as e:
            logger.info(f"Unable to match origin of {ct_mask.get_filename()} to origin of {ct_img.get_filename()}!")

            
        

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
 

def main(argv):
    dir_ = FLAGS.dir
    print(dir_)
    if contains_subdir(dir_):
        print("Recieved a batch directory of multiple patients.")
        for subdir in get_subdirs(dir_):
            print(f"Processing patient {subdir[5:]}")
            process(patient_dir=subdir)
    else:
        print("Recieved a directory of single patient.")
        print(f"Processing patient {dir_[5:]}")
        process(patient_dir=dir_)


if __name__ == "__main__":
    app.run(main)
