def approve(request_info):
    '''
    The function for auto-postponing all the user flowspace requests.
    @param request_info: a dictionary containing the following key-value pairs:
        @key req_ip_addr: @value: requested IP address x.x.x.x - string
        @key req_mac_addr: @value: requested MAC address xx:xx:xx:xx:xx:xx - string
        @key user_last_name: @value: the last name of user - string
        @key user_first_name: @value: the first name of user - string
        @key user_email: @value: email address of the user - string
        @key remote_addr: @value: the IP address of the user when requesting the flowpsace (x.x.x.x) - string
    @return: An array of dictionaries that specifies the limitations on approved flowpsaces.
    Each element in the returned array is treated as one approved flowspace.
    each dictionary has the following possible key-value pairs:
        @key: can be any of the following strings, as in a FlowSpace object:
        "mac_src_s", "mac_src_e"
        "mac_dst_s", "mac_dst_e"
        "eth_type_s", "eth_type_e"
        "vlan_id_s", "vlan_id_e"
        "ip_src_s", "ip_src_e"
        "ip_dst_s", "ip_dst_e"
        "ip_proto_s", "ip_proto_e"
        "tp_src_s", "tp_src_e"
        "tp_dst_s", "tp_dst_e"
        @value: should be an integer in the correct range for each field
    @note: The approved flowpscae should be a strict subset of requested flowspace.
    @note: To POSTPONE the decision for a manual consideration, return None
    @note: to REJECT/Approve NOTHING return an empty array
    '''
    
    return None