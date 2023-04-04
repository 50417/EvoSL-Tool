function [nodeandchangetype_count_map] = get_nodeandchangetype_count_map(obj)
        nodetype_changetype_count_query = ['Select Node_Type,' ...
                ' Case ' ...
                    ' WHEN is_deleted > 0 THEN "Deleted" ' ...
                    ' WHEN is_added > 0 THEN "Added" ' ...
                    ' WHEN (is_modified = 1 and is_renamed=0) THEN "Modified" ' ...
                    ' WHEN (is_modified = 0 and is_renamed=1) THEN "Renamed" ' ...
                    ' WHEN (is_modified = 1 and is_renamed=1) THEN "ModifiedRenamed" ' ...
                ' END AS change_type,' ...
                'totalCount  FROM (	' ...
                ' SELECT Node_Type, is_deleted, is_added, is_modified, is_renamed, count(*) as totalCount' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE is_deleted = 1' ...
                ' or is_added = 1' ...
                ' or is_modified = 1' ...
                ' or is_renamed = 1' ...
                ' group by Node_Type, is_deleted, is_added, is_modified, is_renamed);'];
        result = fetch(obj.conn, nodetype_changetype_count_query);
        [rows,~] = size(result);
        nodeandchangetype_count_map = containers.Map('KeyType','char','ValueType','double');
        for r = 1:rows
            node_type = result{r,1};
            change_type = result{r,2};
            map_key = [char(node_type) '_' char(change_type)];
            total_count = result{r,3};
            nodeandchangetype_count_map(map_key) = total_count;
        end
end

