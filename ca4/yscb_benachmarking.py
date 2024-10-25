import subprocess

# Variables
YCSB_DIR = "/path/to/YCSB"
MYSQL_PROPS = "mysql.properties"
MONGODB_PROPS = "mongodb.properties"
WORKLOAD = "workloads/workloada"

def run_ycsb(db_type, props_file):
    print(f"Running YCSB workload for {db_type}...")
    load_cmd = f"{YCSB_DIR}/bin/ycsb load {db_type} -s -P {WORKLOAD} -P {props_file}"
    run_cmd = f"{YCSB_DIR}/bin/ycsb run {db_type} -s -P {WORKLOAD} -P {props_file}"
    
    subprocess.run(load_cmd, shell=True, check=True)
    subprocess.run(run_cmd, shell=True, check=True)

# Run YCSB for MySQL
run_ycsb("jdbc", MYSQL_PROPS)

# Run YCSB for MongoDB
run_ycsb("mongodb", MONGODB_PROPS)
