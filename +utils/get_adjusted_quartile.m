function [adjusted_quartile] = get_adjusted_quartile(sorted_values,total_num_of_ele,n)
%GET_MEDIAN take nx1 cell array with int values 
%   Detailed explanation goes here
    [no_of_elements,~] = size(sorted_values);
    quartile = n*(total_num_of_ele+1)/4;
    first_idx = floor(quartile);
    second_idx = quartile - first_idx;

    first_ele = 0;
    second_ele = 0; 
    cur_idx = first_idx - (total_num_of_ele - no_of_elements) + 1;
    cur_idy = first_idx - (total_num_of_ele - no_of_elements) + 2;

    if cur_idx >= 1 && cur_idx <= no_of_elements
        first_ele = first_ele + sorted_values{cur_idx,1};
    end

     if cur_idy >= 1 && cur_idy <= no_of_elements
        second_ele = second_ele + sorted_values{cur_idy,1};
    end
    adjusted_quartile = first_ele + (second_ele - first_ele)* second_idx;
            
   
end

