%%% Analyze XDF file from Saccade Study
%   by Jamie Dunkle, 
%   August 2019, UBC Vision Lab
%   Modifications and Additions performed by RM October, 2019
%   Analysis no longer fails if one of the LSL streams is absent
%   Visualization of data improved, segregated plots for X and Y gaze data 

%% Setup
clc 
clear all 

SRATE = 250;
ISI = 1/SRATE;

[xdf_fname, xdf_path] = uigetfile('..\Data\*.xdf', 'Select a File');

xdf = load_xdf([xdf_path, xdf_fname]);

% Initialize variables
event_idx = NaN;
elink_idx = NaN;
opbci_idx = NaN;
[~, strm_idx_count] = size(xdf);
event_strm_exist = false;
elink_strm_exist = false;
opbci_strm_exist = false;

% Search XDF struct to identify streams
for i=1:strm_idx_count
    if strcmp(xdf{1,i}.info.name, 'EventMarkers')
        event_idx = i;   event_strm_exist = true;
    elseif strcmp(xdf{1,i}.info.name, 'EyeLink')
        elink_idx = i;   elink_strm_exist = true;
    elseif strcmp(xdf{1,i}.info.name, 'MyEOGCircuit') %MyEOGCircuit  OpenBCI_EOG
        opbci_idx = i;   opbci_strm_exist = true;
    end
end

% Check for errors in XDF streams
if (event_strm_exist && isnan(event_idx)) || (elink_strm_exist &&...
        isnan(elink_idx)) || (opbci_strm_exist && isnan(opbci_idx))
    error('The data seems to be corrupted. Please check the ''xdf'' stucture to determine the problem.')
end

%% Extract Data

%%% Read EyeLink Data from XDF %%%
if elink_strm_exist
   elink = xdf{1,elink_idx};
   el_time_axis = elink.time_stamps;
   el_dat_x = elink.time_series(1,:);
   el_dat_y = elink.time_series(2,:);
   el_dat_x(el_dat_x < 0) = NaN;
   el_dat_x(el_dat_x > 1920) = NaN;
   el_dat_y(el_dat_y < 0) = NaN;
   el_dat_y(el_dat_y > 1080) = NaN;
elseif ~elink_strm_exist
   elink = NaN; el_time_axis = NaN; el_dat_x = NaN; el_dat_y = NaN;
   el_dat_x(el_dat_x < 0) = NaN; el_dat_x(el_dat_x > 1920) = NaN;
   el_dat_y(el_dat_y < 0) = NaN; el_dat_y(el_dat_y > 1080) = NaN;
end

%%% Read OpenBCI Data from XDF %%%

if opbci_strm_exist
    
    opbci = xdf{1,opbci_idx};
    
    if ~isempty(opbci.time_series)
        ob_time_axis = opbci.time_stamps;
        ob_dat_x = opbci.time_series(1,:);
        ob_dat_y = opbci.time_series(2,:);
    end
    
elseif ~opbci_strm_exist
    opbci = NaN;     
    ob_time_axis = NaN;
    ob_dat_x = NaN;  
    ob_dat_y = NaN;
end

     
%%% Instatiate Event Data %%%

if event_strm_exist
    event = xdf{1,event_idx};
    ev_ts = event.time_stamps;
    ev_dat = event.time_series;
elseif ~event_strm_exist
    event = NaN;
    ev_ts = NaN;
    ev_dat = NaN;
end

%% Plot Data 

% Create time axis
% t1 = min([el_time_axis(1), ob_time_axis(1), ev_ts(1)]);
% t2 = max([el_time_axis(end), ob_time_axis(end), ev_ts(end)]);
% x = 0:ISI:(t2-t1);
t1 = min([el_time_axis(1), ev_ts(1)]);


el_time_axis = el_time_axis - t1;
ob_time_axis = ob_time_axis - t1;
ev_ts = ev_ts - t1;

fig=figure;

B = 1/10*ones(10,1);
outMovingAverage = filter(B,1,detrend(ob_dat_x));

hold on;
plot(el_time_axis, el_dat_x, 'Color', [0, 0.447, 0.741]);
plot(ob_time_axis, outMovingAverage,'Color', [0.635 0.078 0.184]);
title('Horizontal Gaze');
xlabel('Time (secs)');
ylabel('Gaze Position (pixels)');
hold off
legend({'EyeLink X', 'EOG X'}, 'AutoUpdate', 'off');

%% Plot Event Markers

h = gca;
for ii=1:length(ev_ts)
    event_tag = event.time_series{ii};
    event_tag_split = strsplit(event_tag,'_');
    if startsWith(event_tag_split{1}, 'TRIAL') ||...
            startsWith(event_tag_split{1}, 'CALIBH')|| startsWith(event_tag_split{1}, 'CALIBV')
        if strcmp(event_tag_split{end}, 'START')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0.1 0.8 0.1])
        elseif strcmp(event_tag_split{end}, 'PING')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0 1 1])
        elseif strcmp(event_tag_split{end}, 'END')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[1 0 0])
        end
    end
end


%% Plot y
fig=figure;

B = 1/10*ones(10,1);
outMovingAverageV = filter(B,1,detrend(ob_dat_y));

hold on;
plot(el_time_axis, el_dat_y, 'Color', [0, 0.447, 0.741]);
plot(ob_time_axis, outMovingAverageV,'Color', [0.635 0.078 0.184]);
title('Vertical Gaze');
xlabel('Time (secs)');
ylabel('Gaze Position (pixels)');
hold off
legend({'EyeLink Y', 'EOG Y'}, 'AutoUpdate', 'off');

%% Plot Event Markers

h = gca;
for ii=1:length(ev_ts)
    event_tag = event.time_series{ii};
    event_tag_split = strsplit(event_tag,'_');
    if startsWith(event_tag_split{1}, 'TRIAL') ||...
            startsWith(event_tag_split{1}, 'CALIBH') || startsWith(event_tag_split{1}, 'CALIBV')
        if strcmp(event_tag_split{end}, 'START')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0.1 0.8 0.1])
        elseif strcmp(event_tag_split{end}, 'PING')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0 1 1])
        elseif strcmp(event_tag_split{end}, 'END')
            line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[1 0 0])
        end
    end
end

%% Old Code
% %%% Create Subplot for Gaze X Data %%%
% subplot(2,1,1); 
% hold on;
% plot(el_time_axis, el_dat_x, 'Color', [0, 0.447, 0.741]);
% plot(ob_time_axis, detrend(ob_dat_x),'Color', [0.635 0.078 0.184]);
% title('Horizontal Gaze');
% xlabel('Time (secs)');
% ylabel('Gaze Position (pixels)');
% hold off
% legend({'EyeLink X', 'EOG X'}, 'AutoUpdate', 'off');
% 
% %%% Create Subplot for Gaze Y Data %%%
% subplot(2,1,2);
% hold on;
% plot(el_time_axis, el_dat_y, 'Color', [0.929, 0.694, 0.125]);
% plot(ob_time_axis, detrend(ob_dat_y), 'Color', [0.494, 0.184, 0.556]);
% title('Vertical Gaze')
% xlabel('Time (secs)')
% ylabel('Gaze Position (pixels)')
% hold off
% legend({'EyeLink Y', 'EOG Y'}, 'AutoUpdate', 'off');


% for jj = 1:2
%     subplot(2,1,jj)
%     h = gca;
% for ii=1:length(ev_ts)
%     event_tag = event.time_series{ii};
%     event_tag_split = strsplit(event_tag,'_');
%     if startsWith(event_tag_split{1}, 'TRIAL')
%         if ~strcmp(event_tag_split{2}, 'CALIBH') % && strcmp(event_tag_split{2}, 'exp')
%             if strcmp(event_tag_split{4}, 'START')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0.1 0.8 0.1])
%             elseif strcmp(event_tag_split{4}, 'PING')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0 1 1])
%             elseif strcmp(event_tag_split{4}, 'END')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[1 0 0])
%             end
%         elseif strcmp(event_tag_split{2}, 'CALIBH')
%             if strcmp(event_tag_split{length(event_tag_split)}, 'START')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0.1 0.8 0.1])
%             elseif strcmp(event_tag_split{length(event_tag_split)}, 'PING')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim,'Color',[0 1 1])
%             elseif strcmp(event_tag_split{length(event_tag_split)}, 'END')
%                 line([ev_ts(ii) ev_ts(ii)], h.YLim, 'Color',[1 0 0])
%             end
%         end
%     end
% end
% end


% subplot(2,1,2);
% % hax2=axes;
% hold on
% % plot(el_time_axis,el_dat_x);
% % title('Eye Movement HREF - Raw Data')
% xlabel('Time (secs)')
% % ylabel('HREF Value')
% plot(ob_time_axis, ob_dat_filt)
% h=findobj(gcf,'type','axes');
% for ii=1:length(ev_ts)
%     event_tag = event.time_series{ii};
%     event_tag_split = strsplit(event_tag,'_');
%     if ~strcmp(event_tag_split{1}, 'cal') && ~strcmp(event_tag_split{1}, 'exp')
%         if strcmp(event_tag_split{3}, 'start')
%             line([ev_ts(ii) ev_ts(ii)],get(h(1),'YLim'),'Color',[0.1 0.8 0.1])
%         elseif strcmp(event_tag_split{3}, 'end')
%             line([ev_ts(ii) ev_ts(ii)],get(h(1),'YLim'),'Color',[1 0 0])
%         end 
%     end
% end

% T = readtable('C:\Users\Visionlab\Documents\Processing\OpenBCI_GUI\OpenBCI_GUI\SavedData\OpenBCI-RAW-2019-03-06_14-18-11.txt',...
%         'Delimiter',',','ReadVariableNames',false);
% EOG_dat = T.Var3;
% EOG_ts = T.Var13;
% EOG_ts = datenum(EOG_ts);
% 
% [~,idx] = min(abs(EOG_dat-ob_dat_raw(end)));
% bci_dat_raw = EOG_dat(idx-length(ob_dat_raw)+1:idx)';
% figure;hold on;plot(eog_raw_dat);plot(ob_dat_raw)
% 
% EEGDa_ts = [];
% for i = 1:length(VarName13)
%     EEGDa_ts = strsplit(VarName13(1),',');
% end
