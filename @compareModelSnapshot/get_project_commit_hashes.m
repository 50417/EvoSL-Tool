function [child_parent_version_sha,project_id] = get_project_commit_hashes(obj,project_url)
%GET_PROJECT_COMMIT_HASHES Summary of this function goes here
   
    conn = sqlite( obj.project_commit_db,'connect');
    % Getting project id
    project_id_sql = strcat('select project_id from Root_Projects where project_url = "',project_url,'"');
    obj.WriteLog(strcat("SQL Project ID : ",project_id_sql));
    results = fetch(conn,project_id_sql);
    if width(results) ~= 1
        obj.WriteLog(strcat("Error finding ",project_url," in ",obj.project_commit_db));
        error(["Error finding " project_url " in " obj.project_commit_db]);
    end
    project_id = results{1,1};
    
     obj.WriteLog(strcat("Resultant Project ID : ",int2str(project_id)));
    
    %getting project commits parent child sha
    child_parent_sha_sql = strcat('select distinct hash, parents from model_commits where project_id =',int2str(project_id), " order by committer_date");
    obj.WriteLog(strcat("SQL Child Parent Hashes : ",child_parent_sha_sql));
    child_parent_version_sha = fetch(conn,child_parent_sha_sql);
    
    
    
    
end

