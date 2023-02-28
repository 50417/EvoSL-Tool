function res = compare_two_models(obj,model_before, model_after)
% We compare two models . But if a model file is created or a model file is
% deleted: We have to take those changes into consideration. We do that by
% comparing the same files ( one file whose content has been removed and
% other is entact). We found comparing with blank Simulink files will
% introduce some false changes (related to configuration)
    delete(strcat(obj.working_dir,"/*"))
    bdclose('all');
    if strcmp(model_before,'blank') 
        if obj.ignoreNewFileAddedOrDeleted
            res = -1;
            return;
        end
         model_before_renamed = obj.add_letter_to_name(model_after,"x");
         model_before_renamed_fp = fullfile(obj.working_dir,model_before_renamed);
         copyfile(model_after,model_before_renamed_fp);
    else
         model_before_renamed = obj.add_letter_to_name(model_before,"x");
         model_before_renamed_fp = fullfile(obj.working_dir,model_before_renamed);
         copyfile(model_before,model_before_renamed_fp);
    end
   
    
    
    if strcmp(model_after,'blank') 
        if obj.ignoreNewFileAddedOrDeleted
            res = -1;
            return;
        end
         model_after_renamed = obj.add_letter_to_name(model_before,"y");
         model_after_renamed_fp = fullfile(obj.working_dir,model_after_renamed);
         copyfile(model_before,model_after_renamed_fp);
    else
         model_after_renamed = obj.add_letter_to_name(model_after,"y");
         model_after_renamed_fp = fullfile(obj.working_dir,model_after_renamed);
         copyfile(model_after,model_after_renamed_fp);
    end
    
    
    
    load_system(model_before_renamed_fp);
    load_system(model_after_renamed_fp);
    try
        if strcmp(model_before,'blank') 
            [model_before_renamed_fp_edit,~] = utils.split_two_last_delim(model_before_renamed_fp,'.'); %removing file extension
            model_before_renamed_fp_edit = erase(model_before_renamed_fp_edit,obj.working_dir);
            model_before_renamed_fp_edit = erase(model_before_renamed_fp_edit,filesep);
            if(bdIsLibrary(model_before_renamed_fp_edit))
                set_param(model_before_renamed_fp_edit,'Lock','off')
            end 
            Simulink.BlockDiagram.deleteContents(model_before_renamed_fp_edit);
            save_system(model_before_renamed_fp_edit);
             obj.WriteLog(sprintf('Before Model is blank '));    
           
        elseif strcmp(model_after,'blank')
            [model_after_renamed_fp_edit,~] = utils.split_two_last_delim(model_after_renamed_fp,'.');
            model_after_renamed_fp_edit = erase(model_after_renamed_fp_edit,obj.working_dir);
            model_after_renamed_fp_edit = erase(model_after_renamed_fp_edit,filesep);
            if(bdIsLibrary(model_after_renamed_fp_edit))
                set_param(model_after_renamed_fp_edit,'Lock','off')
            end 
            Simulink.BlockDiagram.deleteContents(model_after_renamed_fp_edit);
            save_system(model_after_renamed_fp_edit);
            obj.WriteLog(sprintf('After Model is blank '));   
        end
    catch ME
        obj.WriteLog(sprintf('ERROR deleting the components '));                    
        obj.WriteLog(['ERROR ID : ' ME.identifier]);
        obj.WriteLog(['ERROR MSG : ' ME.message]);
        res = -1;
        return;
    end
    
    Edits = slxmlcomp.compare(model_before_renamed_fp, model_after_renamed_fp);
    %plotTree(Edits);
    %summaryOfChanges(Edits, 1);
    if isempty(Edits)
        res = -1;
    else
        res = treeToTable(Edits);
    end
    if isa(res,'double')
        obj.WriteLog(sprintf('ERROR no changes found in %s. Something is wrong.',model_before_renamed_fp));
    else
        [rows,~] = size(res);
        obj.WriteLog(sprintf('Number of changes found in %s: %d',model_before_renamed_fp,rows));
    end
    close_system(model_before_renamed_fp);
    close_system(model_after_renamed_fp);
    delete(strcat(obj.working_dir,"/*"));
     obj.WriteLog(sprintf('Completed processing %s',model_before_renamed_fp));
end

