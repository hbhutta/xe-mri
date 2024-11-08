import pickle
import ants

with open("testing/reg.pkl", "rb") as file:
    mytx = pickle.load(file)

print(mytx)
   
fixed = ants.image_read('testing/28_proc_ct.nii')
moving = ants.image_read('testing/28_proc_vent.nii')

out = ants.apply_transforms(fixed=fixed, moving=moving, transformlist=mytx['fwdtransforms'])
ants.image_write(image=out, filename='...')
print(out) # None

# moving_ants = ants.image_read(ants.get_data("r16"))
# fixed_ants = ants.image_read(ants.get_data("r27"))
# registration = ants.registration(moving=moving_ants, fixed=fixed_ants, type_of_transform="SyN")
# 
# transformed_normal = ants.apply_transforms(
#     fixed=fixed_ants,
#     moving=moving_ants,
#     transformlist=registration['fwdtransforms'],
#     )
# 
# print(transformed_normal)
# 