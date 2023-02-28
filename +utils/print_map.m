function print_map(map_obj)
%PRINT_MAP Summary of this function goes here
%   Detailed explanation goes here
k = keys(map_obj); 
for i = 1:length(k)
disp("=======================================");
disp(k{i});
disp(map_obj(k{i}))

disp("=======================================");
end
end

