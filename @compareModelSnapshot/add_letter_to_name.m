function renamed_model = add_letter_to_name(obj,model_full_path,letter)
%RENAM Summary of this function goes here
%   Detailed explanation goes here
    [~,file,ext] = fileparts(model_full_path);
    renamed_model = append(file,letter,ext);
end

