def get_all_py_pid() -> tuple[int]:
    """
    Get all python process ids running on the system.

    :return: tuple: A tuple containing the process ids of all python processes running on the system.
    """
    # Get all python processes running on the system
    command = "ps aux | grep python main.py"
    python_processes = [
        p.info["pid"]
        for p in psutil.process_iter(attrs=["pid", "name"])
        if "python" in p.info["name"].lower()
    ]

    return tuple(python_processes)
