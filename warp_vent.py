import ants
import pickle
import os 

def warp_image(fixed, moving, transform_list, interpolation='linear'):
    '''
    Use transforms from registration process to warp an image to target.  For example, if you register the ventilation mask to the CT mask,
    you can use the transforms to warp the ventilation intensity image to the CT space.    

    Parameters
    ----------
    moving : str
        path to fixed image defining domain into which the moving image is transformed
    fixed : str
        path to target image.
    transform_list : list
        list of transforms ***in following order*** [1Warp.nii.gz,0GenericAffine.mat] 
    interpolation : str
            linear (default)
            nearestNeighbor
            multiLabel for label images but genericlabel is preferred
            gaussian
            bSpline
            cosineWindowedSinc
            welchWindowedSinc
            hammingWindowedSinc
            lanczosWindowedSinc
            genericLabel use this for label images

    Returns
    -------
    image warped to target image.

    '''
    ants_fixed = ants.image_read(fixed)
    ants_moving = ants.image_read(moving)

    trans = ants.apply_transforms(fixed=ants_fixed, 
                                  moving=ants_moving,
                                  transformlist=transform_list,
                                  interpolator=interpolation, 
                                  imagetype=0,
                                  whichtoinvert=None, 
                                  defaultvalue=0, verbose=True)
    if interpolation in ['nearestNeighbor', 'multiLabel', 'genericLabel']:
        trans[trans < 1] = 0
    return trans


def warp_vent(ct: str, patient: str, vent: str) -> None:
    print(f"ct {ct} | vent {vent} | patient {os.path.basename(patient)}")

    with open(patient + f"/{os.path.basename(patient)}_reg.pkl", "rb") as file:
        mytx = pickle.load(file)
        print(mytx)

    warped_vent = warp_image(fixed=ct, moving=vent,
                             transform_list=mytx['fwdtransforms'])
    try:
        assert warped_vent != None
    except AssertionError as e:
        print(f"warped_vent has value {
              warped_vent} and type {type(warped_vent)}")
        print(e)
        
    try:
        print(type(warped_vent))
        filename = f"{patient}/{os.path.basename(patient)}_warped_{os.path.basename(vent)}"
        ants.image_write(image=warped_vent, filename=filename)
    except AttributeError as e:
        print(warped_vent)

