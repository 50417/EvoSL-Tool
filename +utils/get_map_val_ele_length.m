function res = get_map_val_ele_length(map_obj)
%GET_MAP_VAL_ELE_LENGTH Summary of this function goes here
k = keys(map_obj); 
res  = 0; 
for i = 1:length(k)
 map_key = k{i};
 map_vals = map_obj(map_key);
 res = res + size(map_vals);

end
end

