# -*- coding: utf-8 -*-
"""
// aolabs.ai software >ao_core/Arch.py (C) 2023 Animo Omnis Corporation. All Rights Reserved.

Thank you for your curiosity!
"""
import time
import sys
import subprocess
import streamlit as st
## // Basic Recommender  -- Reference Design #0
# 
#
# For interactive visual representation of this Arch:
#    https://miro.com/app/board/uXjVM_kESvI=/?share_link_id=72701488535
#
# Cutomize and upload this Arch to our API to create Agents: https://docs.aolabs.ai/reference/kennelcreate
#
try:
    # Attempt to import the package
    import ao_core as ao

except ModuleNotFoundError:
    # If not found, attempt to install the package
    try:
        github_pat = st.secrets["GITHUB_PAT"]
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", f"git+https://{github_pat}@github.com/aolabsai/ao_core"],
            check=True,  # Ensures an error is raised for non-zero exit codes
            capture_output=True,  # Capture output to debug if necessary
            text=True  # Output as string instead of bytes
        )
        print(result.stdout)  # Optional: Print the standard output for debugging
        print(result.stderr)  # Optional: Print the error output for debugging

        # Try importing again after successful installation
        import ao_core as ao

    except subprocess.CalledProcessError as e:
        print(f"Installation failed with error code {e.returncode}")
        print(f"Command output: {e.output}")
        print(f"Error output: {e.stderr}")
        raise  # Re-raise the error after logging details


description = "Basic Recommender System"

#genre, length,  Fnf
arch_i = [4,2,1]     
arch_z = [10]           
arch_c = []           
connector_function = "full_conn"

# To maintain compatability with our API, do not change the variable name "Arch" or the constructor class "ao.Arch" in the line below (the API is pre-loaded with a version of the Arch class in this repo's main branch, hence "ao.Arch")
Arch = ao.Arch(arch_i, arch_z, arch_c, connector_function, description)


