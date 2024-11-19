function [save_path] = scaleNifti(nifti_filename, scale)
    r = niftiread(nifti_filename);
    r_s = imresize3(r, scale);
    [path, name, ~] = fileparts(nifti_filename);
    save_path = fullfile(path, strcat(name, "_scaled.nii"));
    niftiwrite(r_s, save_path);
end

function resize(input_dir, files_to_scale)
    num_files = length(files_to_scale); % Number of files to scale
    scale_factor = 2; % Scale factor

    for i = 1:num_files
        path = fullfile(mri_files(i).folder, mri_files(i).name);
        start_message = sprintf('Scaling file %s by scale factor %d', path, scale_factor)
        disp(start_message);

        save_path = scaleNifti(path, scale_factor);

        end_message = sprintf('The file %s has been scaled by a factor of %d and saved to %s', path, scale_factor, save_path);
        disp(end_message);
    end
end