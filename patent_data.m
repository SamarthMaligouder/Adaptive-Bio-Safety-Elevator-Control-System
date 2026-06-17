% ==========================================
% PATENT SIGNAL GENERATOR
% Creates the "patent_data.mat" file for Simulink
% ==========================================
clear; clc;

% 1. Define Time Axis (0 to 60 seconds)
t = [0, 10, 10.1, 40, 40.1, 60]'; 

% 2. Create "Temp_Input" (Fever Scenario)
% Normal (36.6) -> Jump to Fever (38.5) at 10s -> Back to Normal at 40s
temp_values = [36.6, 36.6, 38.5, 38.5, 36.6, 36.6]';

% 3. Create "Radar_Input" (Occupancy)
% Empty (0) -> Occupied (1) at 10s -> Empty (0) at 40s
radar_values = [0, 0, 1, 1, 0, 0]';

% 4. Create the Dataset Object
ds = Simulink.SimulationData.Dataset;

% Add Temperature Signal
sig1 = timeseries(temp_values, t);
sig1.Name = 'Temp_Input';
ds = ds.addElement(sig1);

% Add Radar Signal
sig2 = timeseries(radar_values, t);
sig2.Name = 'Radar_Input';
ds = ds.addElement(sig2);

% 5. Save to MAT file
save('patent_data.mat', 'ds', '-v7.3');
disp('SUCCESS: patent_data.mat has been created!');