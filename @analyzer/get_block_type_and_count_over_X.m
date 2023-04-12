function [blk_type_name, blk_count] = get_block_type_and_count_over_X(obj,X)

         block_type_and_count_query = ['SELECT * FROM ' ... 
                ' (SELECT count(*) cnt, block_type ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type != "" ' ...
                ' GROUP BY block_type)' ...
                ' WHERE cnt > ' int2str(X) ...
                ' ORDER BY cnt desc'];
         
        result = fetch(obj.conn, block_type_and_count_query);
        [rows,~] = size(result);
        
        blk_count = [];
        subsys_idx = -1;
        for r = 1:rows
            blk_count = [blk_count result{r,1}];  
            if strcmp(result{r,2},'SubSystem')
                subsys_idx = r;
            end
        end
        % result(:,2)
        blk_type_name = result{:,2}';
        if subsys_idx ~= -1
            block_type_and_count_query = ['SELECT count(*) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type = "SubSystem" ' ...
                ' AND block_path LIKE "%DocBlock"'];
             result = fetch(obj.conn, block_type_and_count_query);
             doc_blk_cnt = result{1,1};
             
              block_type_and_count_query = ['SELECT count(*) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type = "SubSystem" ' ...
                ' AND block_path LIKE "%Model Info"'];
             result = fetch(obj.conn, block_type_and_count_query);
             mdl_info_blk_cnt = result{1,1};
             
             blk_count(subsys_idx) = blk_count(subsys_idx) - doc_blk_cnt - mdl_info_blk_cnt;
             if doc_blk_cnt > X
                blk_count = [blk_count doc_blk_cnt];
                [blk_count, idx] = sort(blk_count,'descend');
                new_len = length(blk_count);
                idx_to_be_right_shift = -1;
                for i = 1:new_len
                    if idx(i) == new_len
                        idx_to_be_right_shift =i;
                    end
                end
                if idx_to_be_right_shift ~= -1
                    blk_type_name(1,new_len) = {''};
                    blk_type_name(1,idx_to_be_right_shift+1:new_len) = blk_type_name(1,idx_to_be_right_shift:new_len-1);
                    blk_type_name(1,idx_to_be_right_shift) = {'DocBlock'};
                end
             end 
             if mdl_info_blk_cnt > X 
                 blk_count = [blk_count mdl_info_blk_cnt];
                [blk_count, idx] = sort(blk_count,'descend');
                new_len = length(blk_count);
                idx_to_be_right_shift = -1;
                for i = 1:new_len
                    if idx(i) == new_len
                        idx_to_be_right_shift =i;
                    end
                end
                if idx_to_be_right_shift ~= -1
                    blk_type_name(1,new_len) = {''};
                   blk_type_name(1,idx_to_be_right_shift+1:new_len) = blk_type_name(1,idx_to_be_right_shift:new_len-1);
                    blk_type_name(1,idx_to_be_right_shift) = {'Model Info'};
                end
             
             end
        
            
        end
        
end

