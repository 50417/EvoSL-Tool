function plot_and_print_results(obj)
    nodeandchangetype_count_map = obj.get_nodeandchangetype_count_map();
    node_type = {'block','line','port','mask','annotation','configuration'};
    change_type = {'Renamed','Modified','Deleted','Added'};
    node_changetype_matrix = [];
    for i = 1:length(node_type)
        tmp_vector = obj.get_vector_per_node_type(node_type{i},nodeandchangetype_count_map);
        node_changetype_matrix = [node_changetype_matrix; tmp_vector];
    end
    
    utils.print_latex_compatible_table(node_changetype_matrix,"Element\ChangeType",change_type,node_type,true);
    plot.plot_stacked_bar(node_changetype_matrix,node_type);   
    
    ytick = [0:25000:100000];
    ylimits = [0 125000];
    y_label = 'Total number of changes';
    [blk_type_name, blk_count] = obj.get_block_type_and_count_over_X(50);
    plot.plot_bar(blk_type_name,blk_count,15000,90,90,ytick,ylimits,y_label);

    len_blk_type_name = length(blk_type_name);
    if verLessThan('matlab','9.7')% 2019a
        project_ids= obj.get_project_ids();
        [rows, ~] = size(project_ids);
        for i=1:rows
            project_id = project_ids{i,1};
            obj.get_x_quartile_block_change_per_project_per_commit(project_id);
        end
    end 
    % Only tested on R2022b
    if ~verLessThan('matlab', '9.13')
        normalized_count = [];
        blk_type_distinct_count = obj.get_distinct_block_count_per_type();
        all_keys = keys(blk_type_distinct_count);
        for r = 1:len_blk_type_name
            blk_type_key = blk_type_name(r);
            if contains(blk_type_key,all_keys)
                normalized_count = [normalized_count cast(blk_type_distinct_count(blk_type_key),'double')/cast(blk_count(r),'double')];
            
            else
                error("Error. Investigaate")
            end
        
        
        end

        [normalized_block_count, normalized_sorted_idx] =  sort(normalized_count,'descend');

        normalized_block_name = blk_type_name(normalized_sorted_idx);
        plot.plot_bar(normalized_block_name,normalized_block_count,0.2,90,90,[0:1],[0 1.5],"Normalized change");


        

        [changetype,x_quartile_no_of_change] = obj.get_x_quartile_block_change_per_commit(3);
        disp(changetype); % 75th percentile
        disp(x_quartile_no_of_change);
      
        [changetype,x_quartile_no_of_change] = obj.get_x_quartile_block_change_per_commit(3.2);%80th percentile
        [x_quartile_no_of_change,indices] = sort(x_quartile_no_of_change,'descend'); 
        new_change_type = repmat({''},size(changetype));
        for i = 1:length(changetype)
            new_change_type(i) = changetype(indices(i));
        end
        new_change_type = new_change_type(1:min(length(changetype),10));
        x_quartile_no_of_change = x_quartile_no_of_change(1:min(length(changetype),10));
       
        
        plot.plot_bar(new_change_type,x_quartile_no_of_change,1,75,1,[0:4:26],[0 29],['75th Percentile' newline 'of changes per commit']);
        
        obj.WriteLog("This can take a long time dependent on the number of element changes. ")
        [category, category_change_percent] = obj.get_blocktype_blockpath_count();
        [~,sorted_idx] = sort(category_change_percent);

        for i = length(sorted_idx):-1:1
            idx = sorted_idx(i);
            fprintf("& %s & %s",category{idx},num2str(category_change_percent(idx)) );

            if mod(i,2) == 1
                fprintf(" \\\\ \n")
            end
        end
        plot.plot_bubblechart(category,category_change_percent);
       
         [doc_changes,doc_type] = obj.get_documentation_changes_percent();
         utils.print_latex_compatible_table(doc_changes,"",doc_type,{'Percentage'});
    end
end

