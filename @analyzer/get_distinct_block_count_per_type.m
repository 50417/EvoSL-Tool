function [blk_type_distinct_count] = get_distinct_block_count_per_type(obj)
        blk_type_distinct_count = containers.Map();
        distnct_block_type_and_count_query = [' SELECT count(Distinct block_path) cnt, block_type ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type != "" ' ...
                ' GROUP BY block_type' ...
                ];
         
        result = fetch(obj.conn, distnct_block_type_and_count_query);
        [rows,~] = size(result);
        
        blk_count = [];
        subsys_idx = -1;
        for r = 1:rows
            blk_type_distinct_count(result{r,2}) = result{r,1};
            if strcmp(result{r,2},'SubSystem')
                subsys_idx = r;
            end
        end
        if subsys_idx ~= -1
            block_type_and_count_query = ['SELECT count(Distinct block_path) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type = "SubSystem" ' ...
                ' AND block_path LIKE "%DocBlock"'];
             result = fetch(obj.conn, block_type_and_count_query);
             doc_blk_cnt = result{1,1};
              blk_type_distinct_count('DocBlock') = doc_blk_cnt ;
               
              block_type_and_count_query = ['SELECT count(Distinct block_path) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type = "SubSystem" ' ...
                ' AND block_path LIKE "%Model Info"'];
             result = fetch(obj.conn, block_type_and_count_query);
             mdl_info_blk_cnt = result{1,1};
             blk_type_distinct_count('Model Info')=mdl_info_blk_cnt;
               
             
             blk_type_distinct_count('SubSystem') = blk_type_distinct_count('SubSystem') - doc_blk_cnt - mdl_info_blk_cnt;
                    
     
        end
        
end



