"""
SuperMerger UI Components Registry

This module holds references to Gradio UI components so they can be accessed
across different modules. Components are assigned during UI creation in 
on_ui_tabs() and used by GenParamGetter.py to set up click handlers.

Component Groups:
-----------------
MERGE BUTTONS (used by GenParamGetter._setup_click_events):
    merge, mergeandgen, gen - Main tab merge buttons
    merge2, mergeandgen2, gen2 - Duplicate tab merge buttons
    
XY PLOT BUTTONS (used by GenParamGetter._setup_click_events):
    s_reserve, s_reserve1 - Reserve buttons for XY plot
    gengrid - Generate grid button
    s_startreserve - Start reserve button
    rand_merge - Random merge button

LORA TAB (used by frompromptb click handler in supermerger.py):
    frompromptb - "Get from prompt" button
    sml_loranames - [CheckboxGroup, Textbox, hidden_bool] for LoRA selection

SETTINGS GROUPS (used as inputs to merge functions):
    msettings - Merge settings (model paths, ratios, etc.)
    esettings1 - Extended settings
    genparams - Generation parameters (prompt, steps, etc.)
    hiresfix - Hires fix settings
    lucks - Random/luck merge settings
    xysettings - XY plot settings

OTHER:
    currentmodel - Currently loaded model indicator
    dfalse, dtrue - Hidden bool components for function flags
    id_sets - ID settings
    submit_result - Merge result output
    imagegal - Image gallery outputs
    numaframe - XY plot frame output
"""

# =============================================================================
# MERGE BUTTONS - Click handlers set up in GenParamGetter._setup_click_events()
# Reads: msettings, esettings1, genparams, hiresfix, lucks, currentmodel, txt2img_params
# Writes: submit_result, currentmodel, imagegal
# =============================================================================
merge = None          # Main "Merge!" button
mergeandgen = None    # "Merge and Gen" button  
gen = None            # "Gen" button (generate only)
merge2 = None         # Duplicate tab "Merge!" button
mergeandgen2 = None   # Duplicate tab "Merge and Gen" button
gen2 = None           # Duplicate tab "Gen" button

# =============================================================================
# XY PLOT BUTTONS - Click handlers in GenParamGetter._setup_click_events()
# Reads: xysettings, msettings, genparams, hiresfix, lucks, txt2img_params
# Writes: numaframe, submit_result, currentmodel, imagegal
# =============================================================================
s_reserve = None      # Reserve button for XY plot
s_reserve1 = None     # Reserve button (duplicate)
gengrid = None        # Generate grid button
s_startreserve = None # Start reserve button
rand_merge = None     # Random merge button

# =============================================================================
# LORA TAB - "Get from prompt" functionality
# frompromptb.click in supermerger.py, reads txt2img prompt via JavaScript
# Writes: sml_loranames
# =============================================================================
frompromptb = None    # "Get from prompt" button
sml_loranames = None  # [sml_loras CheckboxGroup, sml_loranames Textbox, hidenb hidden]

# =============================================================================
# SETTINGS GROUPS - Used as inputs to smergegen() and simggen()
# Assigned in supermerger.on_ui_tabs()
# =============================================================================
msettings = None      # Merge settings list
esettings1 = None     # Extended settings component
genparams = None      # Generation parameters list
hiresfix = None       # Hires fix settings list
lucks = None          # Random merge settings list
xysettings = None     # XY plot settings list

# =============================================================================
# OUTPUT COMPONENTS - Written by merge/gen functions
# =============================================================================
currentmodel = None   # Current model indicator (read/write)
submit_result = None  # Merge result textbox
imagegal = None       # Image gallery outputs
numaframe = None      # XY plot frame

# =============================================================================
# UTILITY COMPONENTS - Hidden bool values for function parameters
# =============================================================================
dfalse = None         # Hidden component with value=False
dtrue = None          # Hidden component with value=True
id_sets = None        # ID settings component
