from sets import Set

def grabIndex(many, idx):
    return many[int(idx)]

def generate_grab_index_str(node_id, port_idx):
    """
    Generates a name for a grab index helper node in the graph
    @param node_id the name of the node as string
    @param port_idx the port index
    @return a string containing the node name for the helper node
    """
    return "grabIndex-of-" + str(node_id) + "_" + str(port_idx)

def generate_node_str(node_name, function_name, arguments):
    """
    Generates a dask node
    @param node_name the name of the node as string with surrounding '' e.g. 'NodeName'
    @param function_name the name of the function to be called as string
    @param arguments a list of arguments as strings including surrounding '' if referencing another node
    @return a string looking like the following %node_name%:(%function_name%, %arg1%, ..., %argn%)
    """
    node_str = node_name
    node_str += ":"
    node_str += "("
    node_str += function_name
    for arg in arguments:
        node_str += ","
        node_str += str(arg)
    node_str += ")"

    return node_str

def generate_imports(workflow):
    """
    Identifies all used services and will generate a formatted import block.
    @param workflow the workflow
    @return import_block formatted string with needed imports
    """
    services = Set()
    import_block = "import ServiceUtility\n"
    for node in workflow.get("nodes"):
        service = node.get("service")
        services_len_before = len(services)
        services.add(service.get("id"))
        #checking if add was successful
        if(len(services) > services_len_before):
            import_block += "import " + service.get("id") + ".v" + str(service.get("version")) + "." + service.get("id") + "\n"
    return import_block

def get_leaf_nodes(workflow):
    """
    Identifies all nodes that have no connection to the right
    @param workflow the workflow
    @return a list of all nodes that have no connection to the right
    """
    workflow_nodes = Set()
    connected_nodes = Set()
    for node in workflow.get("nodes"):
        workflow_nodes.add(node.get("id"))
        for connection in node.get("connections"):
            if(connection is not None and connection.get("port_idx") >= 0):
                #The node that is associated is a connected node
                connected_nodes.add(connection.get("node_id"))
    return workflow_nodes.symmetric_difference(connected_nodes)

def generate_identifier_methods(nodes, primary_key):
    s = ""
    for node in nodes:
        s += "def identifier_{}():\n".format(node.get("id"))
        s += "  return [{}, \"{}\"]\n".format(primary_key, node.get("id"))
    return s

def generate_dsk_representation(node, added_grabber_nodes):
    """
    Generates the dask representation of a peach workflow node including helper nodes
    @param node a dict containing the data according to the workflow.avsc
    @param added_grabber_nodes a helper list containing already added helper nodes
    @return a string representing the dask nodes generated
    @return an updated version of added_grabber_nodes
    """
    currentIdParam = "identifier_{}".format(node.get("id"))
    currentIdParamString = "'{}'".format(currentIdParam)
    node_str = ""
    print node.get("connections")
    if(node.get("connections")):
        node_str += "{}:({},),\n".format(currentIdParamString, currentIdParam)
        node_name = "\'" + node.get("id") + "\'"
        #resolve service script and function and place it here
        function_name = str(node.get("service").get("id")) + ".v" + str(node.get("service").get("version")) + "." + str(node.get("service").get("id")) + ".start"
        arguments = [currentIdParamString]
        for connection in node.get("connections"):
            if(connection is not None):
            #by convention negative ports indicate that the node_id points to data e.g. a filepath
               if (connection.get("port_idx") >= 0):
                    grabber_node_name = "\'" + generate_grab_index_str(connection.get("node_id"), connection.get("port_idx")) + "\'"
                    if(grabber_node_name not in added_grabber_nodes):
                        added_grabber_nodes.add(grabber_node_name)
                        connection_node = "\'" + connection.get("node_id") + "\'"
                        grabber_node_args = []
                        grabber_node_args.append(connection_node)
                        grabber_node_args.append(connection.get("port_idx"))
                        grabber_node  = generate_node_str(grabber_node_name, "ServiceUtility.grabIndex", grabber_node_args)
                        node_str += grabber_node
                        node_str += ",\n"
                    arguments.append(grabber_node_name)
               else:
                    #simply add the node name
                    arguments.append("\'" + connection.get("node_id") + "\'")
            else:
                #We will not have an argument (no node and no filepath thus we add None)
                arguments.append("None")
        for param in node.get("parameters"):
            if param is not None:
                arguments.append("'{}'".format(param))
            else:
                arguments.append("None")
        node_str += generate_node_str(node_name, function_name, arguments)
    return node_str, added_grabber_nodes

def glue_graph(node_strings):
    """
    Glues all nodes together
    @param node_strings the generated node strings
    @return dsk generated code representing dask graph variable
    """
    dsk = "dsk = {"
    for ns in node_strings[:-1]:
        dsk += str(ns)
        dsk += ",\n"
    dsk += node_strings[-1] + "\n"
    dsk +="}"
    return dsk

def generate_sys_paths(service_utility_path, library_path):
    import os
    s = "import sys\nsys.path.insert(0, '{}')\n".format(service_utility_path)
    s += "sys.path.insert(0, '{}')\n".format(library_path)
    s += "sys.path.insert(0, '{}')\n".format(os.path.join(library_path, "library", "ServiceUtility"))
    return s


def generate_dask_script(workflow, service_hub_path, library_path, primary_key):
    """
    Generates a string representing a formatted dask script
    @workflow dict representing the workflow based on workflow.avsc
    @return the dask script string representation
    """
    node_strings = []
    #Variable to identify already added helper/grabber nodes
    added_grabber_nodes = Set()
    for node in workflow.get("nodes"):
        node_rep, added_grabber_nodes = generate_dsk_representation(node, added_grabber_nodes)
        node_strings.append(node_rep)
    dsk_script = generate_sys_paths(service_hub_path, library_path)
    dsk_script += generate_imports(workflow)
    dsk_script += generate_identifier_methods(workflow.get("nodes"), primary_key)
    dsk_script += glue_graph(node_strings)
    dsk_script += "\n" + "from dask.multiprocessing import get\n"
    dsk_script += "\nServiceUtility.update_status({}, 1)\n".format(primary_key)
    dsk_script += "\nServiceUtility.create_temp_folder({})\n".format(primary_key)
    dsk_script += "\ntry:\n"
    for node in get_leaf_nodes(workflow):
        dsk_script += "  get(dsk, " + "'" + node + "'" + ")\n"
    dsk_script += "  ServiceUtility.update_status({}, 3)\n".format(primary_key)
    dsk_script += "except Exception as e:\n"
    dsk_script += "  print(str(e))\n"
    dsk_script += "  ServiceUtility.update_status({}, 4)\n".format(primary_key)
    dsk_script += "\nServiceUtility.update_progress({}, 100)\n".format(primary_key)
    dsk_script += "\nServiceUtility.update_end_time({})".format(primary_key)
    dsk_script += "\nServiceUtility.upload_output({})".format(primary_key)
    return dsk_script
