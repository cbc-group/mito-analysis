import glob
import os

target_dir = 'G:/Vins/Mito_Binarization/11292017/c6_zp3_7ms_1s/rawpoints'
extension = 'am'
insert_at = 322

# list files in the folder
file_list_in = glob.glob(os.path.join(target_dir, f'*.{extension}'))

# shift frames
file_list_out = []
for path in file_list_in:
    # extract filename
    parent, fname = os.path.split(path)
    fname, fext = os.path.splitext(fname)

    # separate frame id
    tokens = fname.split('_')
    tokens, frame = tokens[:-1], int(tokens[-1])

    if frame >= insert_at:
        # we need to shift
        frame += 1
        # reconstruct filename
        suffix = '_'.join(tokens)
        fname = f'{suffix}_{frame:04d}{fext}'
        path = os.path.join(parent, fname)    
    
    # save it
    file_list_out.append(path)

# batch rename
for f_in, f_out in zip(reversed(file_list_in), reversed(file_list_out)):
    if f_in == f_out:
        continue
    os.rename(f_in, f_out)
