function [project_ids_res] = get_project_ids(obj)
%GET_PROJECT_IDS Summary of this function goes here
%   Detailed explanation goes here
    project_ids_sql = strcat("SELECT DISTINCT project_id from ",char(obj.table_name));
    project_ids_res = fetch(obj.conn, project_ids_sql);
end

