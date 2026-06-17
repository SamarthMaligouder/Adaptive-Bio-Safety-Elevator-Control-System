% =========================================================================
% PATENT VALIDATION PARAMETERS: ADAPTIVE BIO-SAFETY ELEVATOR
% =========================================================================
clear; clc;

% --- 1. System Timing ---
Ts = 0.01;                  % Simulation Time Step (10ms resolution)
Sim_Duration = 60;          % Total Test Duration (seconds)

% --- 2. Sensor Thresholds (Section 21 of Patent) ---
Temp_Fever_Limit = 37.8;    % deg C (Fever Threshold)
Temp_Normal = 36.6;         % deg C (Healthy Baseline)
Radar_Sensitivity = 0.5;    % V (Voltage threshold for movement)

% --- 3. Logic Weights (Section 18.b Formula) ---
W_t = 50;                   % Weight for Fever (High priority)
W_c = 10;                   % Weight for Coughs
W_d = 0.5;                  % Weight for Duration (Low priority)
Risk_Trigger_Level = 45;    % Score required to start "Deep Clean"

% --- 4. Safety Interlock Specs ---
UV_Cutoff_Latency = 0.05;   % Max hardware delay (50ms)
UV_Voltage = 12;            % Operating Voltage for LEDs

disp('>> System Parameters Loaded. Ready to build Simulink Model.');