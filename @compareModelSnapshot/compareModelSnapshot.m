classdef compareModelSnapshot
    %COMPAREMODEL Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        proj_commit_snapshot_folder;
        project_name; %Project name is the name of the project when downloaded GitHub zip is extracted 
        working_dir;
        project_commit_db = '/home/sls6964xx/Downloads/Github_Simulink.sqlite'; %location to project commits dabatase
        ignoreNewFileAddedOrDeleted = false; 
        colnames = {'Before_Project_SHA','After_Project_SHA','Model',...
            'Block_Path','Node_Type','Block_Type',...,
            'is_deleted','is_modified','is_added','is_renamed'};
        coltypes = {'VARCHAR','VARCHAR','VARCHAR',...
             'VARCHAR','VARCHAR','VARCHAR',...
            'BOOLEAN','BOOLEAN','BOOLEAN','BOOLEAN'};
        conn;
        table_name;
        logfilename;
        blk_category_map;
        child_parent_version_sha;
    end
    
    methods
        function obj = compareModelSnapshot(model_comparison_utility_folder,project_loc_or_url, varargin)
            % model_comparison_utility_folder : https://zenodo.org/record/6410073#.Y1Ggm9LMJhE / Version 1.4 is used in this study
            % if project_loc_or_url = project location in the local file system: note that github projectm downloaded as zip wont work 
            % varargin must be the github project url 
            
       
  
            obj.proj_commit_snapshot_folder = 'proj_commit_snapshot_folder';
            %obj.project_name = project_name;
            obj.working_dir = 'workdir';
            obj.logfilename = strcat('Model_Snapshot_Compare',datestr(now, 'dd-mm-yy-HH-MM-SS'),'.txt');

            obj.WriteLog('open');
     
        
            if(~exist(obj.working_dir,'dir'))
                    mkdir(obj.working_dir);
            end
            if(~exist(obj.proj_commit_snapshot_folder,'dir'))
                    mkdir(obj.proj_commit_snapshot_folder);
            end
            db = strcat("model_compare_new",datestr(now, 'dd-mm-yy-HH-MM-SS'),".sqlite");
            
            
            obj.table_name = "Model_Comparison_Across_Commit";
            obj.conn = obj.connect_db_and_create_table(db,obj.table_name);
            
            
            
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
           obj.child_parent_version_sha = obj.get_project_commit_hashes(project_url);
            %Block Category
            
            block_lib_map = utils.getblock_library_map();
            block = keys(block_lib_map);
            obj.blk_category_map = containers.Map();
            categories = java.util.HashSet;
        
            for i = 1:length(block)
                lib = block_lib_map(block{i}); % cell 
                blk_type = block{i};
                category = utils.get_category(blk_type,lib{1},true);
                categories.add(category);
                if ~isKey(obj.blk_category_map,category)
                    obj.blk_category_map(category) = java.util.HashSet;
                    obj.blk_category_map(category).add(blk_type);
                else
                    obj.blk_category_map(category).add(blk_type);
                end
            
            end
            obj.blk_category_map('Structural').add('Reference');
             obj.blk_category_map('Trigger').add('ActionPort');
            utils.print_map(obj.blk_category_map);
           %Adding the utility in the matlab path
           addpath(genpath(model_comparison_utility_folder));
           
        end
        
       
        WriteLog(obj,Data);
        conn = connect_db_and_create_table(obj,db,table_name);
        
        %
        status = setup_before_and_after_project(obj,project_loc_or_url);
        child_parent_version_sha = get_project_commit_hashes(obj,project_url);
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
        
        
        %Replication and plots
        %ChangeType and counts
        nodeandchangetype_count_map = get_nodeandchangetype_count_map(obj);
        res_vector = get_vector_per_node_type(obj, node_type,nodeandchangetype_count_map);
        
        %block Type and counts
        [blk_type_name, blk_count] = get_block_type_and_count_over_20(obj);
       
        %[blocktype_changetype,median_of_change] =
        %get_median_of_block_change_per_commit(obj); DEPRECATED
        [blocktype_changetype,median_of_change] = get_x_quartile_block_change_per_commit(obj,x)
        [changetype,median_no_of_change] = get_median_of_node_change_per_commit(obj,nodetype);
        
        %bubbble chart category change
        [category, category_change_percent] = get_blocktype_blockpath_count(obj);
        replicate_plots_and_results(obj);
        
        %Documentation Changes
        [doc_changes,doc_type] = get_documentation_changes_percent(obj);
    end
end

