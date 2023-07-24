function driver(dependenc,project_commit_db,use_URL,project_location )
    %dependenc = ''; % Download and extract https://zenodo.org/record/6410073#.ZDX-JNLMK-Z
    %project_commit_db = ''; % Db where all the metadata is collected. OR use EvoSL.sqlite
    %project_location = ''; % where all git projects are stored OR EvoSL project directory
    proj_commit_snapshot_folder = "/tmp/proj_commit_snapshot_folder";
    %use_URL = true;
    
    
    conn = sqlite( project_commit_db,'connect');
    % Getting project id
    % change SQL as you see fit.
    project_id_sql = strcat('select * from (select * from project_commit_summary order by model_commits desc limit 50)');
    results = fetch(conn,project_id_sql);
    
    x = [results{:,1}];
    %x = x';
    conn = utils.connect_db(project_commit_db);
    
    n = length(x);
    
    for i = 1:n
        if(exist(proj_commit_snapshot_folder,'dir'))
            rmdir(proj_commit_snapshot_folder,'s');
        end
        sprintf("=============DOING %d out of %d============",i,n);
        sql = strcat("SELECT project_url from Root_Projects where project_id = ",int2str(x(i)));
         result = fetch(conn, sql);
         [rows,~] = size(result);
    
        if use_URL
            m_obj = compareModelSnapshot(proj_commit_snapshot_folder,project_commit_db, dependenc,result{rows,1});
        else
         
         proj_loc = strcat(project_location,filesep,int2str(x(i)));
        m_obj = compareModelSnapshot(proj_commit_snapshot_folder,project_commit_db, dependenc,proj_loc,result{rows,1});
        end
        m_obj.process_project();
        rmdir(proj_commit_snapshot_folder,'s');
        sprintf("=============DONE %d out of %d============",i,n);
    end
end