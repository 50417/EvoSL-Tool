function [category, category_change_percent] = get_blocktype_blockpath_count(obj)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
 block_type_path_count_query =     [  'SELECT count(*) cnt, block_type,block_path ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE Block_Type != ""' ...
                ' GROUP BY block_type,block_path' ...
                ' ORDER BY block_type'
                ];
            
        result = fetch(obj.conn, block_type_path_count_query);
        [rows,~] = size(result);
        
        category_change_map = containers.Map(); 

        for r = 1:rows
            blk_count = result{r,1};
            blk_type = result{r,2};
            blk_path = result{r,3};
            
            return_category = utils.get_category(blk_type,blk_path,false,obj.blk_category_map);
            %if strcmp(return_category,'Others')
            %    disp(blk_type);
            %end
           if ~isKey(category_change_map,return_category)
                category_change_map(return_category) = 0;
           end
            category_change_map(return_category) = category_change_map(return_category) + blk_count;
        end
        
        k = keys(category_change_map);
        %utils.print_map(category_change_map);
        category = cell(1,length(rows)); 
        category_change_count = zeros(1,length(rows)); 
        for i = 1:length(k) 
           category(1,i) = k(i);
           category_change_count(1,i) = category_change_map( k{i});
        end
        category_change_percent = round(category_change_count/sum(category_change_count)*100,2);
        
        
end

