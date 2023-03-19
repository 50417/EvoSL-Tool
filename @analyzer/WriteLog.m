  function WriteLog(obj,Data)
        global FID % https://www.mathworks.com/help/matlab/ref/global.html %https://www.mathworks.com/help/matlab/ref/persistent.html Local to functions but values are persisted between calls.
        if isempty(FID) & ~strcmp(Data,'open')

             FID = fopen(['logs' filesep obj.logfilename], 'a+');
        end
        % Open the file
        if strcmp(Data, 'open')
            mkdir('logs');
          FID = fopen(['logs' filesep obj.logfilename], 'a+');
          if FID < 0
             error('Cannot open file');
          end
          return;
        elseif strcmp(Data, 'close')
          fclose(FID);
          FID = -1;
        end
        try
            fprintf(FID, '%s: %s\n',datestr(now, 'dd/mm/yy-HH:MM:SS'), Data);
        catch ME
            ME;
        end
        % Write to the screen at the same time:
        
            fprintf('%s: %s\n', datestr(now, 'dd/mm/yy-HH:MM:SS'), Data);
 
end
        
