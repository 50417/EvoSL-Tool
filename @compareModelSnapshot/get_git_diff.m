function [list_of_diff_files] = get_git_diff(obj,before_sha,after_sha,project_loc)
%GET_GIT_DIFF This function returns listof Simulink model files changed
%between two commits
%   Detailed explanation goes here
    
    list_of_diff_files = {};
      %https://stackoverflow.com/questions/62591772/why-does-git-diff-tree-tree-ish-not-print-a-result-when-applied-to-the-very
   
    if isempty(before_sha)
        before_sha = '--root';
    end
    
    cur_dir = pwd;
    % git diff-tree behaviours is different from git diff / For example
    % --diff-filter=R is not recognized by diff-tree . avoid R(rename) and
    % T (type changed)
   command = strcat("TERM=ansi git --no-pager diff -r --name-only ",before_sha," ",after_sha," --diff-filter=ACDMUXB");
    obj.WriteLog(sprintf("Getting diff using command : %s",command));
    
    cd(project_loc);
    
    [status,cmdoutput] =  system(command);  
    
    cd(cur_dir);
    obj.WriteLog(sprintf("Getting diff Status (0 means success): %d",status));
    if status~= 0
        obj.WriteLog(sprintf("Error running the command"));
        pause();
    end
    
    
    
    potential_list_of_changed_files = splitlines(strtrim(cmdoutput));
    for i = 1: length(potential_list_of_changed_files)
        if contains(potential_list_of_changed_files{i},'.mdl') || contains(potential_list_of_changed_files{i},'.slx')
            list_of_diff_files(end+1) = potential_list_of_changed_files(i);
        end
        
    end
    

end

