function [model_files_list] = get_list_of_sim_model(obj,project)
   model_slx = dir(fullfile(project,obj.project_name,'**/*.slx')); 
   num_model_slx = length(model_slx);
   
   model_mdl = dir(fullfile(project,obj.project_name,'**/*.mdl')) ;
   num_model_mdl = length(model_mdl);
   total_model = num_model_slx+num_model_mdl;
   
   model_files_list = strings(1,total_model);
   for i = 1:total_model
       if i<=num_model_slx
           project_path_split = split(model_slx(i).folder,project);
           relative_project_path = project_path_split{2}; 
            model_files_list(i) = fullfile(relative_project_path,model_slx(i).name);
       else
           project_path_split = split(model_mdl(i-num_model_slx).folder,project);
           relative_project_path = project_path_split{2}; 
           model_files_list(i) = fullfile(relative_project_path,model_mdl(i-num_model_slx).name);
       end
   end

end
