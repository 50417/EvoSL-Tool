function res_obj = add_value_to_map(map_obj,map_key, val)

%ADD_VALUE_TO_MAP Adds value to the first non_zero col 
    row_vector = map_obj(map_key);
    [~,cols] = size(row_vector);
    for i = 1:cols
        if row_vector(i)==0
            row_vector(i) = val;
            break;
        end
    end
    map_obj(map_key) = row_vector;
    res_obj = map_obj; 
    
end

