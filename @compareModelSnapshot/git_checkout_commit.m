function git_checkout_commit(obj,commit_sha,project_loc)
%GIT_CHECKOUT_COMMIT Summary of this function goes here
%   Detailed explanation goes here
 cur_dir = pwd;
 checkout_cmd = strcat("git checkout -f " ,commit_sha);
 obj.WriteLog(sprintf("Checking out in %s: %s",project_loc,commit_sha));
 
 cd(project_loc);
 
 
 status = system(checkout_cmd);
 
 cd(cur_dir);
 obj.WriteLog(sprintf("Checking out Status: %d",status));
 
 if status ~= 0
    error('Error checking out');
 end
end

