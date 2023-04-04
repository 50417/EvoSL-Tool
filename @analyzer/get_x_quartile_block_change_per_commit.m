function [blocktype_changetype,median_of_change] = get_x_quartile_block_change_per_commit(obj,x)
%GET_BLOCK_CHANGE_PER_COMMIT Summary of this function goes here
%   Detailed explanation goes here
    block_change_query = [
                    ' SELECT *, row_number() OVER (PARTITION  BY Block_Type, change_type order by totalCount) rn,'...
                    ' count(*) over (PARTITION by Block_Type, change_type) counter'...
                    ' FROM ('...
                    ' SELECT'... 
                    ' parent_sha, child_sha, Block_Type,'...      
                    ' CASE'...  
                    ' WHEN is_deleted > 0 THEN "Deleted"'...  
                    ' WHEN is_added > 0 THEN "Added"  '...
                    ' WHEN is_modified > 0 THEN "Modified"  '...
                    ' WHEN is_renamed > 0 THEN "Renamed"'...  
                    ' END AS change_type,totalCount  '...
                    ' FROM (	'... 
                    ' SELECT parent_sha, child_sha, Block_Type, is_deleted, is_added, is_modified, is_renamed, count(*) as totalCount'... 
                    ' FROM ' char(obj.table_name) ...
                    ' WHERE( is_deleted = 1 or is_added = 1 or is_modified = 1 or is_renamed = 1 ) '...
                    ' AND node_type = "block"'...
                    ' GROUP BY parent_sha, child_sha,Block_Type, is_deleted, is_added, is_modified, is_renamed) '...
                    ' ORDER BY Block_Type,change_type, totalCount)'...
                   ];
            obj.WriteLog(sprintf('SQL for getting changes %s',block_change_query));    
        result = fetch(obj.conn, block_change_query);
        [rows,~] = size(result);
         
        median_of_change = [];%zeros(1,min(rows,10));
         blocktype_changetype = {};%cell(1,min(rows,10));
         start_idx = 1;
         
         total_num_of_model_commits_query = ['select count(distinct child_sha) from ' char(obj.table_name)];
         total_num_of_model_commits_result = fetch(obj.conn, total_num_of_model_commits_query);
         total_num_of_model_commits = total_num_of_model_commits_result{1,1};
         
         idx_counter = 1;
        while start_idx <= rows
            
            end_idx = result{start_idx,7} + start_idx - 1;
            sorted_values = result(start_idx:end_idx,5);
            % TODO: Remove hardcoded 583 model commits and get from database
            median_adj_val = utils.get_adjusted_quartile(sorted_values,total_num_of_model_commits,x);
            if median_adj_val > 0
                blockandchangeType = [char(result{start_idx,3}) ' ' char(result{start_idx,4})];
                blocktype_changetype{1,idx_counter} = blockandchangeType;

                median_of_change(1,idx_counter) = median_adj_val;
                idx_counter = idx_counter + 1;
            end
            
            
            
            start_idx = end_idx + 1;
            
                    
        end


end


