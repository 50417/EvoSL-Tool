function print_latex_compatible_table(data,rows_cols_heading, cols_heading_cell_arr,rows_heading_cell_arr,add_total )
%PRINT_LATEX_COMPATIBLE_TABLE Summary of this function goes here
%   Detailed explanation goes here
     if ~exist('add_total','var')
     % third parameter does not exist, so default it to something
      add_total = false;
    end
    [rows,cols] = size(data);
    fprintf('%s',rows_cols_heading);
    for i = 1:cols
        fprintf(" & %s",cols_heading_cell_arr{i});
    end
    fprintf(" \\\\ \n");
    for i = 1:rows
        fprintf("%s",rows_heading_cell_arr{i});
        total = 0;
        for j = 1: cols
            if ismatrix(data)
                total = total + data(i,j);
                fprintf(" & %s",utils.add_comma_to_num(data(i,j)));
            else
                total = total + data{i,j};
                fprintf(" & %s",utils.add_comma_to_num(data{i,j}));
            end
        end
        %Also add total 
        if add_total
            fprintf(" & %s",utils.add_comma_to_num(total));
        end
        fprintf(" \\\\ \n");
    end
end

