function [status] = setup_before_and_after_project(obj, project_loc_or_url)
%SETUP_BEFORE_AND_AFTER_PROJECT Summary of this function goes here
%   Detailed explanation goes here
        [~,isValidURL] = urlread(project_loc_or_url);
        
        if exist(fullfile(obj.proj_commit_snapshot_folder,'Before')) && exist(fullfile(obj.proj_commit_snapshot_folder,'After'))
            obj.WriteLog(['Before/After folder not empty.  Project may be already cloned/copied : Moving to comparison. Try deleting ' obj.proj_commit_snapshot_folder ' to clone again.']);
            status = 0;
            return 
        end
        if isValidURL == 1 %The provided string is a github project url
            before_command = strcat('git clone ',{' '}, project_loc_or_url,{' '},fullfile(obj.proj_commit_snapshot_folder,'Before'));
            before_command = before_command{1}; % converting ell array to string
            obj.WriteLog(strcat('Cloning with command:',before_command));
            status = system(before_command);
            if status == 1% clone failed
                return
            end
            
            after_command =  strcat('git clone ',{' '}, project_loc_or_url,{' '},fullfile(obj.proj_commit_snapshot_folder,'After'));
            after_command = after_command{1};
            obj.WriteLog(['Cloning with command ' after_command]);
            status = system(after_command);
        else %The provided string is a github project in your local file system
            before_folder = fullfile(obj.proj_commit_snapshot_folder,'Before');
            after_folder = fullfile(obj.proj_commit_snapshot_folder,'After');
            if ~exist(before_folder)
                mkdir(before_folder);
            end
            if ~exist(after_folder)
                mkdir(after_folder);
            end
            copyfile(project_loc_or_url,before_folder);
            copyfile(project_loc_or_url,after_folder);
            status = 0;
        end
end

