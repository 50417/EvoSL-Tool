classdef analyzer
    %ANALYZER Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        model_evol_db = '';% update this database with model_evol sqlite db
        
        table_name;
        conn;
        logfilename;
        blk_category_map;
    end
    
    methods
        function obj = analyzer()
            %ANALYZER Construct an instance of this class
            %   Detailed explanation goes here
            obj.conn = utils.connect_db(obj.model_evol_db);
            obj.table_name = "Model_Evolution";
            obj.logfilename = strcat('analyzer_log',datestr(now, 'dd-mm-yy-HH-MM-SS'),'.txt');

            obj.WriteLog('open');
            
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
            
        end
        %
        WriteLog(obj,Data);
        
        %plots and results 
        
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
        plot_and_print_results(obj);
        
        %Documentation Changes
        [doc_changes,doc_type] = get_documentation_changes_percent(obj);
    end
end

