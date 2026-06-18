% =========================================================================
% PATENT VALIDATION SUITE: ADAPTIVE BIO-SAFETY ELEVATOR
% FILE: patent_master_setup.m
% =========================================================================
% clear; clc;

% 1. Simulation Parameters
Ts = 0.01;              % Sample Time (10ms resolution)
T_Final = 100;          % 100 Seconds Simulation
time = 0:Ts:T_Final;

% 2. SENSOR INPUT GENERATION
% -------------------------------------------------------------------------
% A. RADAR OCCUPANCY (Logic: 1=Occupied, 0=Empty)
% Passenger 1 (Healthy) enters at 10s, leaves at 30s.
% Passenger 2 (Infected) enters at 50s, leaves at 80s.
Radar_Signal = zeros(size(time));
Radar_Signal(time >= 10 & time <= 30) = 1; 
Radar_Signal(time >= 50 & time <= 80) = 1;

% B. THERMAL CAMERA INPUT (Degrees Celsius)
% Baseline = 22C (Empty Room)
Temp_Signal = 22 * ones(size(time));
Temp_Signal(time >= 10 & time <= 30) = 36.6; % Healthy Body Temp
Temp_Signal(time >= 50 & time <= 80) = 38.9; % High Fever

% C. COUGH SENSOR (Impulses)
% Infected passenger coughs at T=60s and T=70s
Cough_Signal = zeros(size(time));
Cough_Signal(abs(time - 60) < 0.1) = 1; 
Cough_Signal(abs(time - 70) < 0.1) = 1;

% D. TOUCH TRACKING (Button ID: 0=None, 1-4=Buttons)
% Healthy passenger touches Button 2 at T=20s
% Infected passenger touches Button 4 at T=75s
Touch_Signal = zeros(size(time));
Touch_Signal(abs(time - 20) < 0.2) = 2;
Touch_Signal(abs(time - 75) < 0.2) = 4;

% 3. PACKING DATA FOR SIMULINK
% We create Timeseries objects for "From Workspace" blocks
sim_radar = timeseries(Radar_Signal, time);
sim_temp  = timeseries(Temp_Signal, time);
sim_cough = timeseries(Cough_Signal, time);
sim_touch = timeseries(Touch_Signal, time);

fprintf('>> TEST VECTORS LOADED:\n');
fprintf('   - Scenario A (10s-30s): Healthy Passenger (Expect NO Cleaning)\n');
fprintf('   - Scenario B (50s-80s): Infected Passenger (Expect FULL Decon)\n');
fprintf('>> Ready to run Simulink Model.\n');