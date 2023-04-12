classdef compareModelSnapshot
    %COMPAREMODEL Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        proj_commit_snapshot_folder;
        project_id;
        project_name; %Project name is the name of the project when downloaded GitHub zip is extracted 
        working_dir;
        project_commit_db; %location to project commits dabatase
        model_evol_db;
        
        ignoreNewFileAddedOrDeleted = true; 
        colnames = {'project_id','parent_sha','child_sha','model',...
            'block_path','node_type','block_type',...,
            'is_deleted','is_modified','is_added','is_renamed'};
        coltypes = {'INTEGER','VARCHAR','VARCHAR','VARCHAR',...
             'VARCHAR','VARCHAR','VARCHAR',...
            'BOOLEAN','BOOLEAN','BOOLEAN','BOOLEAN'};
        conn;
        table_name;
        logfilename;
        blk_category_map;
        child_parent_version_sha;
    end
    
    methods
        function obj = compareModelSnapshot(proj_commit_snapshot_folder,project_commit_db,model_comparison_utility_folder,project_loc_or_url, varargin)
            % model_comparison_utility_folder : https://zenodo.org/record/6410073#.Y1Ggm9LMJhE / Version 1.4 is used in this study
            % if project_loc_or_url = project location in the local file system: note that github projectm downloaded as zip wont work 
            % varargin must be the github project url 
            
       
            obj.project_commit_db = project_commit_db;
            obj.model_evol_db = obj.project_commit_db;
            obj.proj_commit_snapshot_folder = proj_commit_snapshot_folder;
            %obj.project_name = project_name;
            obj.working_dir = 'workdir';
            obj.logfilename = strcat('model_evol_log_',datestr(now, 'dd-mm-yy-HH-MM-SS'),'.txt');

            obj.WriteLog('open');
     
        
            if(~exist(obj.working_dir,'dir'))
                    mkdir(obj.working_dir);
            end
            if(~exist(obj.proj_commit_snapshot_folder,'dir'))
                    mkdir(obj.proj_commit_snapshot_folder);
            end
            
            if strcmp(obj.model_evol_db,"")
                obj.model_evol_db = obj.project_commit_db;
            end
            obj.table_name = "Model_Element_Changes";
            obj.conn = obj.connect_db_and_create_table(obj.model_evol_db,obj.table_name);
            
            
            
            % setting up the project folder 
            status = obj.setup_before_and_after_project(project_loc_or_url);
            if status > 0
                error('INVALID PROJECT URL OR PROJECT FOLDER');
            end
            
            %getting the commit hashes from the database 
           if ~isempty(varargin)
               project_url = varargin{1};
           else 
               project_url = project_loc_or_url;
           end
           
           %Getting project commit version sha
           [obj.child_parent_version_sha,obj.project_id] = obj.get_project_commit_hashes(project_url);
            
           
             %utils.print_map(obj.blk_category_map);
           %Adding the utility in the matlab path
           addpath(genpath(model_comparison_utility_folder));
           
        end
        
        % set up functions
        WriteLog(obj,Data);
        conn = connect_db_and_create_table(obj,db,table_name);
        status = setup_before_and_after_project(obj,project_loc_or_url);
        [child_parent_version_sha,project_id] = get_project_commit_hashes(obj,project_url);
        
        git_checkout_commit(obj,commit_sha,project_loc);
        list_of_diff_files = get_git_diff(obj,before_sha,after_sha,project_loc);
        res = compare_two_models(obj,model_before, model_after);
        
        model_list = get_list_of_sim_model(obj,project_before);
        renamed_model = add_letter_to_name(obj,model_full_path,letter);
        project_sha = get_project_sha(obj,project_after);
        
        output_bol = write_to_database(obj,before_sha, after_sha,model,comparison_res_table);
        
        process_two_project_versions(obj,project_before, project_after,before_commit_sha,...
            after_commit_sha,processed_project_model_commits,list_of_diff_files);  
        process_project(obj);
        
        
        
    end
end

