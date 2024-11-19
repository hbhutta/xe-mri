from utils import split_mask, nib_save 

ct_mask = 'imgs/PIm0028/CT_mask_neg_affine.nii'
imgs = split_mask(mask_image_file_path=ct_mask, return_imgs=True)

for img in imgs:
    nib_save(img=img[0], filename=img[1])