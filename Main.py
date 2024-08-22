# -*- coding: utf-8 -*-
"""
// aolabs.ai software >ao_core/Arch.py (C) 2023 Animo Omnis Corporation. All Rights Reserved.

Thank you for your curiosity!
"""


## // Basic Recommender  -- Reference Design #0
# 
#
# For interactive visual representation of this Arch:
#    https://miro.com/app/board/uXjVM_kESvI=/?share_link_id=72701488535
#
# Cutomize and upload this Arch to our API to create Agents: https://docs.aolabs.ai/reference/kennelcreate
#
import ao_core as ao

description = "Basic Clam"

#genre, length,  Fnf
arch_i = [4,2,1]     
arch_z = [10]           
arch_c = []           
connector_function = "full_conn"

# To maintain compatability with our API, do not change the variable name "Arch" or the constructor class "ao.Arch" in the line below (the API is pre-loaded with a version of the Arch class in this repo's main branch, hence "ao.Arch")
Arch = ao.Arch(arch_i, arch_z, arch_c, connector_function, description)


