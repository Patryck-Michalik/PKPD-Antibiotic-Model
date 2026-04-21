# ===========================
# 1. Import Required Libraries
# ===========================
import numpy as np                     # numerical operations (arrays, math)
from scipy.integrate import solve_ivp  # ODE solver
from scipy.integrate import trapezoid  # numerical integration (AUC)

# ===========================
# 2. Define Model Parameters
# ===========================

# Create a dictionary of model parameters which allows for easy modification of individual parameters
def create_params(
    half_life = 6.0,    # drug half-life (hours)
    V = 1,              # volume of distribution (L)
    r = 0.8,            # bacterial growth rate (1/hour)
    Bmax = 1e9,         # carrying capacity (max bacteria)
    Emax = 1.0,         # maximum kill rate (1/hour)
    EC50 = 0.5,         # concentration for half-max kill (concentration units)
):
    return {
        "half_life": half_life,
        "V": V,
        "r": r,
        "Bmax": Bmax,
        "Emax": Emax,
        "EC50": EC50,
    }

# =============================
# 3. Define Simulation Settings
# =============================

# Creates a dictionary of simulation parameters which allows for easy modification of individual parameters
def create_sim_settings(
    dose_mg = 10,         # dosage for drug in mg
    dose_interval = 12,   # dosing interval in hours
    t_end = 120,          # end timepoint in hours
    B0 = 1e6              # starting bacterial load in CFU/mL
):
    n_doses = int(t_end/dose_interval)  # calculate number of doses based on simulation duration
    
    return {
        "dose_mg": dose_mg,
        "dose_interval": dose_interval,
        "n_doses": n_doses,
        "t_end": t_end,
        "B0": B0
    }

# =====================
# 4. Define PK/PD Model
# =====================

def pkpd_model(t, y, p):
    
    """
    Define the system of ODEs for:
    - drug concentration C(t)
    - bacterial burden B(t)

    Inputs
    ------
    t : float
        Current time
    y : list or array
        Current state values [C, B]
    p : dict
        Parameter dictionary

    Returns
    -------
    [dCdt, dBdt] : list
        Time derivatives for drug concentration and bacterial burden
    """

    # Unpack current state
    C, B = y  # C = drug concentration, B = bacterial burden

    #---------------------------------------------------
    # Pharmacokinetics (PK): one-compartment elimination
    #---------------------------------------------------

    # Convert half-life to elimination rate constant
    # Formula: k_elimination = ln(2)/t_half
    kel = np.log(2) / p["half_life"]

    # First-order elimination - drug concentration decreases exponentially
    # dC/dt = -kel * C
    dCdt = -kel * C

    #------------------------------------------------------
    # Pharmacodynamics (PD): Bacterial Growth and Drug Kill
    #------------------------------------------------------
    
    # Logistic bacterial growth - population grows until reaching carrying capacity
    # growth = r * B * (1 - B/Bmax) where:
    # - r is intrinsic growth rate
    # - Bmax is carrying capacity
    growth = p["r"] * B * (1 - B / p["Bmax"])
    
    # Drug kill effect using Emax model (saturable concentration-effect relationship)
    # kill_rate = (Emax * C)/(EC50 + C) where:
    # - Emax is maximum kill rate
    # - EC50 is concentration producing 50% of maximum effect
    kill_rate = (p["Emax"] * C) / (p["EC50"] + C)

    # Net bacterial dynamics: growth minus death due to drug
    # dB/dt = growth - kill_rate * B
    dBdt = growth - kill_rate * B

    return [dCdt, dBdt]

# ========================
# 5. Simulate PK/PD System
# ========================

def simulate_pkpd(dose_times, dose_amount, params, t_end, B0):
    
    """
    Simulate the PK/PD system under repeated dosing.

    Inputs
    ------
    dose_times : array-like
        Times at which doses are given
    dose_amount : float
        Dose amount (mg)
    params : dict
        Model parameters
    t_end : float
        End time of simulation
    B0 : float
        Initial bacterial burden

     Returns
    -------
    t_all, C_all, B_all : arrays
        Time, concentration, and bacterial burden trajectories
    """
    # Initial state: no drug present, initial bacterial load B0
    y_current = [0.0, B0]  # State vector [drug concentration, bacterial load]
    t_current = 0.0        # Start time of simulation

    # Containers for piecewise simulation output
    t_store, C_store, B_store = [], [], []  # Lists to store time, concentration and bacterial burden

    # Loop through each dosing time
    for dt in dose_times:

        # Integrate from current time up to the next dose time
        if dt > t_current:  # Only simulate if the dose time is in the future
            t_eval = np.linspace(t_current, dt, 120)  # Create 120 evenly spaced time points for evaluation

            # Solve the ODE system from current time to next dose time
            sol = solve_ivp(
                pkpd_model,                # The ODE function defining the model
                (t_current, dt),           # Time span for this segment
                y_current,                 # Current state [C, B]
                args = (params,),          # Model parameters passed to the ODE function
                t_eval = t_eval            # Specific times at which to store the solution
            )

            # Store this segment of the solution
            t_store.append(sol.t)          # Time points
            C_store.append(sol.y[0])       # Drug concentration trajectory
            B_store.append(sol.y[1])       # Bacterial burden trajectory

            # Update the current state to the last point in this segment
            y_current = [sol.y[0, -1], sol.y[1, -1]]  # Extract final values for next segment
            t_current = dt                            # Update current time

        # Apply bolus dose as an instantaneous concentration jump
        y_current[0] += dose_amount / params["V"]  # Add dose (adjusted by volume of distribution)

    # After the final dose, integrate to the end of the simulation
    if t_current < t_end:  # Only if we haven't reached the end time yet
        t_eval = np.linspace(t_current, t_end, 400)  # More dense time points for final segment

        # Solve the final segment of the simulation
        sol = solve_ivp(
            pkpd_model,
            (t_current, t_end),
            y_current,
            args = (params,),
            t_eval = t_eval
        )

        # Store the final segment
        t_store.append(sol.t)
        C_store.append(sol.y[0])
        B_store.append(sol.y[1])

    # Concatenate all simulation segments into full trajectories
    t_all = np.concatenate(t_store)  # Combine all time arrays
    C_all = np.concatenate(C_store)  # Combine all concentration arrays
    B_all = np.concatenate(B_store)  # Combine all bacterial burden arrays

    return t_all, C_all, B_all

# ===================================
# 6. Run a Single Simulation Function
# ===================================

def run_simulation(params = None, sim_settings = None):

    """
    Wrapper function to build a dose schedule and run a single simulation.

    Inputs
    ------
    params : dict or None
        Model parameters; if None, defaults are used
    sim_settings : dict or None
        Simulation settings; if None, defaults are used

    Returns
    -------
    t, C, B : arrays
        Time, concentration, and bacterial burden trajectories
    """

    # Use default parameters if not provided
    if params is None:
        params = create_params()

    # Use default simulation settings if not provided
    if sim_settings is None:
        sim_settings = create_sim_settings()

    # Construct dose times from interval and number of doses
    # Creates an array of evenly spaced time points starting from 0
    # up to (but not including) the product of dose_interval and n_doses
    dose_times = np.arange(
        0,                                              # Start time
        sim_settings["dose_interval"] * sim_settings["n_doses"],  # End time (exclusive)
        sim_settings["dose_interval"]                   # Step size between doses
    )

    # Run the PK/PD simulation with the specified parameters
    # Returns time points, drug concentration, and bacterial burden
    return simulate_pkpd(
        dose_times = dose_times,                        # When doses are administered
        dose_amount = sim_settings["dose_mg"],          # Amount of each dose in mg
        params = params,                                # Model parameters
        t_end = sim_settings["t_end"],                  # End time of simulation
        B0 = sim_settings["B0"]                         # Initial bacterial burden
    )

# ===============================
# 7. Sweep Over a Model Parameter
# ===============================

def run_param_sweep(param_name, values, params=None, base_sim_settings=None):
   
    """
    Sweep over one MODEL parameter (e.g., half_life, EC50, Emax).

    Inputs
    ------
    param_name : str
        Name of parameter to vary
    values : array-like
        Values to test
    base_params : dict or None
        Baseline parameter set; if None, defaults are used
    sim_settings : dict or None
        Fixed simulation settings; if None, defaults are used

    Returns
    -------
    results : dict
        Dictionary containing simulation outputs for each swept value
    """

    # If no base parameters provided, use default model parameters
    if params is None:
        params = create_params()

    # If no simulation settings provided, use default dosing schedule
    if base_sim_settings is None:
        base_sim_settings = create_sim_settings()

    # Dictionary to store results for each parameter value
    results = {}

    # Loop over each value in the sweep
    for val in values:

        # Copy base parameters so we don't overwrite original
        params = params.copy()

        # Replace the selected parameter with the current sweep value
        params[param_name] = val

        # Run simulation with updated parameter
        t, C, B = run_simulation(params = params, sim_settings = base_sim_settings)

        # Compute Summary Metrics

        # Final Bacterial Burden
        final_B = B[-1]

        # Compute Final Log10 Reduction (single number)
        # This measures how many orders of magnitude the bacteria were reduced
        # If bacteria are completely eliminated, use NaN to avoid log(0) error
        log10_reduction = (
            np.log10(base_sim_settings["B0"] / final_B)
            if final_B > 0 else np.nan
        )

        # Compute time-dependent log10 reduction (curve)
        # Set minimum bacterial count to 1 to avoid log(0) errors
        B_eff = np.maximum(B, 1.0)
        log_reduction_t = np.log10(base_sim_settings["B0"] / B_eff)

        # Area Under Curve - measures total drug exposure over time
        auc = trapezoid(C, t)
        
        # Store all simulation outputs and calculated metrics in results dictionary
        results[val] = {
            "params": params,                       # Parameter set used
            "sim_settings": base_sim_settings.copy(), # Simulation settings used
            "t": t,                                 # Time points
            "C": C,                                 # Drug concentration over time
            "B": B,                                 # Bacterial count over time
            "final_B": final_B,                     # Final bacterial burden
            "AUC": auc,                             # Area under concentration curve
            "log10_reduction": log10_reduction,     # Overall log reduction
            "log_reduction_t": log_reduction_t      # Time-dependent log reduction
        }

    return results

# =============================================
# 8. Sweep Over a Simulation Setting
# =============================================

def run_sim_setting_sweep(setting_name, values, params=None, base_sim_settings=None):
    
    """
    Sweep over one SIMULATION setting (e.g., dose_mg, dose_interval, n_doses).

    Inputs
    ------
    setting_name : str
        Name of simulation setting to vary
    values : array-like
        Values to test
    params : dict or None
        Fixed model parameters; if None, defaults are used
    base_sim_settings : dict or None
        Baseline simulation settings; if None, defaults are used

     Returns
    -------
    results : dict
        Dictionary containing simulation outputs for each swept value
    """

    # Use default model parameters if none provided
    if params is None:
        params = create_params()

    # Use default simulation settings if none provided
    if base_sim_settings is None:
        base_sim_settings = create_sim_settings()

    # Dictionary to store results
    results = {}

    # Loop over values of the setting we are sweeping
    for val in values:

        # Copy simulation settings to avoid overwriting original
        sim_settings = base_sim_settings.copy()

        # Replace the setting we are sweeping
        sim_settings[setting_name] = val

        # Special case: adjust number of doses if we're changing dose interval
        if setting_name == "dose_interval":
            sim_settings["n_doses"] = int(sim_settings["t_end"] / val)

        # Run simulation with updated setting
        t, C, B = run_simulation(params=params, sim_settings=sim_settings)

        
        # Compute Summary Metrics
        
        # Extract final bacterial burden
        final_B = B[-1]

        # Compute log10 reduction (difference between initial and final bacterial count)
        # If final_B is 0, set to NaN to avoid log(0) error
        log10_reduction = (
            np.log10(sim_settings["B0"] / final_B)
            if final_B > 0 else np.nan
        )

        # Compute time-dependent log10 reduction (curve)
        # Ensure minimum value of 1.0 to avoid log(0) errors
        B_eff = np.maximum(B, 1.0)
        log_reduction_t = np.log10(sim_settings["B0"] / B_eff)

        # Calculate Area under the Concentration-Time Curve (AUC)
        auc = trapezoid(C, t)

        # Store all results for this parameter value in the results dictionary
        results[val] = {
            "params": params.copy(),
            "sim_settings": sim_settings,
            "t": t,                        # Time points
            "C": C,                        # Drug concentration over time
            "B": B,                        # Bacterial count over time
            "final_B": final_B,            # Final bacterial count
            "AUC": auc,                    # Area under concentration-time curve
            "log10_reduction": log10_reduction,  # Overall log reduction
            "log_reduction_t": log_reduction_t   # Log reduction over time
        }

    return results
