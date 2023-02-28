function [combined_list] = combine_two_list(list1,list2)
%COMBINE_TWO_LIST Summary of this function goes here
%   Detailed explanation goes here
    l1_len = length(list1);
    l2_len = length(list2);
    combined_hashset = containers.Map(); 

    for i = 1:l1_len
        file = list1{i};
        if ~isKey(combined_hashset,file )
            combined_hashset(file) = 1;
        end
    end
    
    for i = 1:l2_len
        file = list2{i};
        if ~isKey(combined_hashset,file )
            combined_hashset(file) = 1;
        end
    end
    file_cell_arr = keys(combined_hashset);
    combined_list = strings(1,length(file_cell_arr));
    for i = 1:length(file_cell_arr)
        combined_list(1,i) = file_cell_arr{i};
    end
end