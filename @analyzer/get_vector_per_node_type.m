function [res_vector] = get_vector_per_node_type(obj, node_type,nodeandchangetype_count_map)
%GET_VECTOR_PER_NODE_TYPE Summary of this function goes here
%   Detailed explanation goes here
    res_vector = [-1 -1 -1 -1];
    change_type = {'Renamed','Modified','Deleted','Added'};
    modified_renamed_change_type = 'ModifiedRenamed';
    for i = 1:4
        map_key = [node_type '_' change_type{i}]; 
        modren_map_key =  [node_type '_' modified_renamed_change_type]; 
        if isKey(nodeandchangetype_count_map,map_key)
            res_vector(i) = nodeandchangetype_count_map(map_key);
        else 
            res_vector(i) = 0;
        end
        if (strcmp(change_type{i},'Renamed') || strcmp(change_type{i},'Modified')) && isKey(nodeandchangetype_count_map,modren_map_key)
            res_vector(i) = res_vector(i) + nodeandchangetype_count_map(modren_map_key);
        end
        
    end
end

