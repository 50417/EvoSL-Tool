function process_two_project_versions(obj,project_before, project_after,project_before_sha,...
    project_after_sha,processed_project_model_commits,list_of_diff_files)
    %The following is deprecated . UNcomment %1 to compare comparing every
    %file in the folder rather than using git diff-tree data. 
    %1model_before_list = obj.get_list_of_sim_model(project_before);
    %1model_after_list = obj.get_list_of_sim_model(project_after);
    
    %1all_models = utils.combine_two_list(model_before_list,mosdel_after_list);
    
    %1project_before_split = split(project_before,filesep);
    %1project_folder_before = project_before_split(end);
    
    %1project_after_split = split(project_after,filesep);
    %1project_folder_after = project_after_split(end);
    
    %project_before_sha = obj.get_project_sha(project_before);
    %obj.WriteLog(sprintf('Before Project SHA = %s',project_before_sha));
    %project_after_sha = obj.get_project_sha(project_after);
    %obj.WriteLog(sprintf('After Project SHA = %s',project_after_sha));
   
    
    for i = 1:numel(list_of_diff_files)%1numel(all_models)
        if ~(endsWith(list_of_diff_files{i},".mdl") || endsWith(list_of_diff_files{i},".slx"))
            continue;
        end
        if ~isempty(processed_project_model_commits) && sum(ismember(processed_project_model_commits,strcat(int2str(obj.project_id),"_",project_before_sha,"_",...
                project_after_sha,"_",list_of_diff_files{i})))>0
            obj.WriteLog(sprintf("Already processed %s",list_of_diff_files{i}));
            continue;
        end
        %1potential_model_project_before = fullfile(project_before,all_models(i));
        %1potential_model_project_after = fullfile(project_after,all_models(i));
        potential_model_project_before = fullfile(project_before,list_of_diff_files{i});
        potential_model_project_after = fullfile(project_after,list_of_diff_files{i});
        
        
        if isfile(potential_model_project_after) && isfile(potential_model_project_before)
            obj.WriteLog(sprintf('Comparing %s',list_of_diff_files{i}));
        elseif ~isfile(potential_model_project_before)
            potential_model_project_before = 'blank';
        elseif ~isfile(potential_model_project_after)
            potential_model_project_after = 'blank';
        else
            error('ERROR');
        end
        try
            %1obj.WriteLog(sprintf('Comparing %s',all_models(i)));
            obj.WriteLog(sprintf('Comparing %s (twice prints mean this is not a new file added/deleted)',list_of_diff_files{i}));
            comparison_res = obj.compare_two_models(potential_model_project_before,potential_model_project_after);
        catch ME
            obj.WriteLog(sprintf('ERROR Comparing models snapshot '));                    
            obj.WriteLog(['ERROR ID : ' ME.identifier]);
            obj.WriteLog(['ERROR MSG : ' ME.message]);
            continue;
        end
        if isa(comparison_res,'table')
            try
                obj.write_to_database(project_before_sha,project_after_sha,list_of_diff_files{i}, ...
                    comparison_res);
            catch ME
                obj.WriteLog(sprintf('ERROR Inserting into database '));                    
                obj.WriteLog(['ERROR ID : ' ME.identifier]);
                obj.WriteLog(['ERROR MSG : ' ME.message]);
                continue;
            end
        end
        
    end

end

