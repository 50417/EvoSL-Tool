function [blocktype_changetype,median_of_change] = get_x_quartile_block_change_per_project_per_commit(obj,project_id)
%GET_BLOCK_CHANGE_PER_COMMIT Summary of this function goes here
%   Detailed explanation goes here
    median_of_change = [];%zeros(1,min(rows,10));
    blocktype_changetype = {};%cell(1,min(rows,10));

    number_of_commits_sql = strcat("SELECT count(DISTINCT child_sha) from ",char(obj.table_name));
    if project_id ~= -1
        number_of_commits_sql = strcat(number_of_commits_sql," WHERE project_id=", int2str(project_id));
    end
    number_of_commits_res = fetch(obj.conn, number_of_commits_sql);
    number_of_commits = number_of_commits_res{1,1};
    if number_of_commits < 180 % looking at smaller projects does not make sense. 
        return;
    end
    if project_id ~= -1
        block_change_query = strcat(' SELECT parent_sha, child_sha, Block_Type, SUM(is_deleted) D, SUM(is_added) A, SUM(is_modified) M, SUM(is_renamed) R ',...
                    " FROM ", char(obj.table_name) , ...
                    ' WHERE project_id = ' ,int2str(project_id) ,' AND node_type = "block" GROUP BY parent_sha, child_sha,Block_Type ', ...
                    ' ORDER BY Block_Type' ...
                 );
    else
    block_change_query = strcat(' SELECT parent_sha, child_sha, Block_Type, SUM(is_deleted) D, SUM(is_added) A, SUM(is_modified) M, SUM(is_renamed) R ',...
                    " FROM ", char(obj.table_name) , ...
                    ' WHERE node_type = "block" GROUP BY parent_sha, child_sha,Block_Type ', ...
                    ' ORDER BY Block_Type' ...
                 );
    end
            obj.WriteLog(sprintf('SQL for getting changes %s',block_change_query));    
        result = fetch(obj.conn, block_change_query);
        [rows,cols] = size(result);
        
        % Fetching data in a hash map
        blocktype_changetype = containers.Map();
        for i = 1: rows
            blocktype = result(i,3);
            added = strcat(blocktype," Added");
           deleted = strcat(blocktype," deleted");
           modified = strcat(blocktype," modified");
            renamed = strcat(blocktype," renamed");
            if ~isKey(blocktype_changetype,added)
                
                blocktype_changetype(added) = zeros(1,number_of_commits);
                blocktype_changetype(deleted) = zeros(1,number_of_commits);
                blocktype_changetype(modified) = zeros(1,number_of_commits);
                blocktype_changetype(renamed) = zeros(1,number_of_commits);
            end
            for j = 4: cols
                val = result{i,j};
                if  val~= 0
                    if j == 4
                        blocktype_changetype = utils.add_value_to_map(blocktype_changetype,deleted,val);
                    elseif j==5
                        blocktype_changetype = utils.add_value_to_map(blocktype_changetype,added,val);
                    elseif j==6
                        blocktype_changetype = utils.add_value_to_map(blocktype_changetype,modified,val);
                    elseif j==7
                        blocktype_changetype = utils.add_value_to_map(blocktype_changetype,renamed,val);
                    end
                end
            end
            
        end
        
        % GEtting medians
        all_keys = keys(blocktype_changetype);
        [~, cols ] = size(all_keys);
        for i = 1:cols
            cur_key = all_keys{1,i};
 
            med_val = median(blocktype_changetype(cur_key));
            if med_val ~=0
                disp(cur_key);
                disp(med_val);
            end
        
        end
        
         
       


end


