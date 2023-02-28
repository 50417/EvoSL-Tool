function [sha] = get_project_sha(obj,project_after)
%Deprecated
    sha_file = fullfile(project_after,"sha.txt");
    sha = strtrim(fileread(sha_file));
    
end

