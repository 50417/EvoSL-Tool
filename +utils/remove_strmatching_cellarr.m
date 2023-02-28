function [inputcellarr] = remove_strmatching_cellarr(inputcellarr,pat, patCount)
%REMOVE_STRMATCHING_CELLARR Removes any elements in the cell array that
% contains pattern with specific count in the cell array
%   inputcellarr: it is a n x1 cell array containing strings
%   pat: pattern can be string  or PATTERN OBJECThttps://www.mathworks.com/help/matlab/ref/pattern.html
    index = count(inputcellarr,pat)==patCount;
    inputcellarr(index) = [];
end