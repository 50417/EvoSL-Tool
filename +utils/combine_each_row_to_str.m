function [combined_str_lst] = combine_each_row_to_str(input_cell_arr,delim)
%COMBINE_EACH_ROW_TO_STR Summary of this function goes here
%   Detailed explanation goes here
    if isempty(input_cell_arr)
        combined_str_lst =  input_cell_arr;
        return;
    end
    [numOfRows,numOfCols] = size(input_cell_arr);
    combined_str_lst = strings(1,numOfRows);
    for i = 1 : numOfRows
        combined_str_lst(1,i) = input_cell_arr{i,1};
        for j = 2: numOfCols
            combined_str_lst(1,i) = strcat(combined_str_lst(1,i),delim,input_cell_arr{i,j});
        end 
        
    end
    
end

