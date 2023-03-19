function process_project(obj)
    child_parent_version_sha = obj.child_parent_version_sha;    
     %all_sub_folders = dir(obj.proj_commit_snapshot_folder);
     %all_sub_folders = all_sub_folders(3:end);
     %sub_folder_num = length(all_sub_folders);
     total_model_snapshots = length(child_parent_version_sha);
     obj.WriteLog(sprintf('Total Number of Model Snapshots = %d',total_model_snapshots));
     
     processing_folder_sql = ['SELECT  DISTINCT project_id, parent_sha, child_sha, model from ' char(obj.table_name) ];
     processed_project_model_commits = utils.combine_each_row_to_str(fetch(obj.conn,processing_folder_sql),'_');
     for i = 1:total_model_snapshots
        obj.WriteLog(sprintf("============================Processing Commit %d (out of %d)=======================",i,total_model_snapshots));
        if contains(child_parent_version_sha{i,2},',')
            obj.WriteLog(sprintf("Skipping Merge commmit:%s",child_parent_version_sha{i,1}));
            continue;
        end
        

        before_commit_sha = child_parent_version_sha{i,2};
        %sanitize string 
        before_commit_sha = erase(before_commit_sha,'[');
        before_commit_sha = erase(before_commit_sha,']');
        before_commit_sha = erase(before_commit_sha,"'");
        after_commit_sha = child_parent_version_sha{i,1};
        
         %Checking out commit sha to the folder
        project_before = fullfile(obj.proj_commit_snapshot_folder,'Before');
        project_after = fullfile(obj.proj_commit_snapshot_folder,'After');
        
        try
            obj.git_checkout_commit(before_commit_sha,project_before);
            obj.git_checkout_commit(after_commit_sha,project_after);
            
        catch ME
            obj.WriteLog(sprintf('ERROR Checkout out  models snapshot %s and %s',before_commit_sha,after_commit_sha));                    
            obj.WriteLog(['ERROR ID : ' ME.identifier]);
            obj.WriteLog(['ERROR MSG : ' ME.message]);
            continue;
        end
       
      
       % if ~isempty(processed_project_model_commits) && sum(contains(processed_project_model_commits,child_parent_version_sha{i,1})) > 0
        %    obj.WriteLog(sprintf("Skipping Processed commmit:%s",child_parent_version_sha{i,1}));
        %    continue;
        %end
        
        %Check if this is empty: otherwise passto subfunuctionm. Pass this to sub
        list_of_diff_files = obj.get_git_diff(before_commit_sha,after_commit_sha,project_after);
        obj.WriteLog(sprintf('Comparing %s and %s ',before_commit_sha, after_commit_sha));
        if isempty(list_of_diff_files)
            obj.WriteLog(sprintf('No simulnk model changes found'));
            continue;
        end
        obj.process_two_project_versions(project_before, project_after,before_commit_sha,...
            after_commit_sha,processed_project_model_commits,list_of_diff_files);


        obj.WriteLog(sprintf('======= Processed commit %d ========= ',i));

     
     end
     
end

